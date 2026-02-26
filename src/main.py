import csv
import sys
from pathlib import Path


def parse_custom_csv_to_md(input_path, output_path):
    """
    複数の表が含まれるCSVを読み込み、個別のMarkdown表として出力する
    """
    with open(input_path, "r", encoding="utf-8-sig") as f:  # BOM付きCSV対策でutf-8-sig
        reader = csv.reader(f)
        rows = list(reader)

    md_lines = []
    current_table_rows = []

    def flush_table():
        """溜まっているテーブル行をMarkdownに変換して出力バッファに追加"""
        if not current_table_rows:
            return

        # テーブルの列数を正規化（各行の列数が違う場合への対策）
        # 1列目がすべて空文字なら、整形のために1列目を削除する（Excel方眼紙対策）
        first_col_empty = all(
            (not r[0].strip()) if r else True for r in current_table_rows
        )

        clean_rows = []
        for r in current_table_rows:
            if first_col_empty and len(r) > 1:
                clean_rows.append(r[1:])
            else:
                clean_rows.append(r)

        if not clean_rows:
            return

        # ヘッダー処理
        header = clean_rows[0]
        # 空のカラム名を埋める（Markdownの崩れ防止）
        header = [h if h.strip() else " " for h in header]

        md_lines.append(f"| {' | '.join(header)} |")
        md_lines.append(f"| {' | '.join(['---'] * len(header))} |")

        # データ行処理
        for row in clean_rows[1:]:
            # 行の長さがヘッダーと合わない場合の調整
            if len(row) < len(header):
                row += [""] * (len(header) - len(row))
            elif len(row) > len(header):
                row = row[: len(header)]

            # 改行コードなどをエスケープ
            row = [cell.replace("\n", "<br>") for cell in row]
            md_lines.append(f"| {' | '.join(row)} |")

        md_lines.append("")  # テーブル後の空行
        current_table_rows.clear()

    # --- 行ごとの解析ループ ---
    for row in rows:
        # 空行判定（すべてのセルが空、またはカンマだけの行）
        is_empty = not any(cell.strip() for cell in row)

        # 有効なデータが入っているセルの数
        filled_cells = [cell for cell in row if cell.strip()]

        if is_empty:
            # 空行に来たら前のテーブルを書き出す
            flush_table()
            continue

        # タイトル行の判定ロジック
        # 条件: 有効なセルが1つだけ、かつ その内容が特定のキーワードではない場合
        if len(filled_cells) == 1:
            # 前のテーブルがあれば書き出す
            flush_table()

            # 見出しとして出力 (例: ### 基本情報)
            title = filled_cells[0]
            md_lines.append(f"### {title}\n")
        else:
            # 通常のテーブルデータ行として蓄積
            current_table_rows.append(row)

    # ループ終了後に残っているテーブルがあれば書き出す
    flush_table()

    # ファイル書き込み
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))


def main():
    files = sys.argv[1:]

    if not files:
        print("CSVファイルをこのexeにドラッグ＆ドロップしてください。")
        input("エンターキーを押して終了します...")
        return

    # exeの場所を基準にする
    base_path = Path(sys.argv[0]).parent
    output_dir = base_path / "Converts"
    output_dir.mkdir(exist_ok=True)

    print(f"保存先: {output_dir}\n")

    for file_path_str in files:
        input_path = Path(file_path_str)
        print(f"変換中: {input_path.name} ...")

        try:
            output_filename = input_path.with_suffix(".md").name
            output_file = output_dir / output_filename

            parse_custom_csv_to_md(str(input_path), str(output_file))

            print(f" -> 完了: {output_filename}")

        except Exception as e:
            import traceback

            traceback.print_exc()
            print(f" -> エラー: {e}")

    print("\nすべての処理が完了しました。")
    input("エンターキーを押して終了します...")


if __name__ == "__main__":
    main()
