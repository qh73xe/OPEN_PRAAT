# OPEN_PRAAT
PRAAT アノテーション支援ツールです。

FOR LINUX なので注意してください。

## 開発環境
python を利用して作成されています。
また、pipenv を前提にしています。
その内、良くするかもですが、とりあえず私がつかえればよいので。

## 導入方法
praat と sendpraat コマンドが使用可能であることを前提とします。
そのうえで、以下のコマンドを実行すると、必要なpythonライブラリが導入されます

```
pipenv install

```

アプリケーションを実行するには以下のコマンドを実施します。

```
pipenv run open_praat

```

## 設定ファイル
このプログラムは現状では設定ファイルを手動で用意する必要があります。
これがないと、どうしようもないので注意です。

設定ファイルは以下のディレクトリに置かれているものとします。

- ~/.config/open-praat/projects/<same project name>/

必要はものは以下の2種類のJSONファイルです。

- gui.json
- filelist.json

gui.json は以下の形式です。


```
{
  "<teir name>": [
      ["<btn1>", "<btn2>"...],
      {"<label>": ["select1", "select2"...]...}
  ]
}

```

リスト型を渡した場合、ボタンになり、辞書型を渡すとセレクトになります。
GUI上では、これらを選択すると選択された文字列がインターバルティアに挿入されます。

filelist.json は以下の形式です。

```
{
  "files": [
      {
        "wav": "<your wav path>",
        "tg": "<your text grid path>"
      },
      ...
  ]
}

```

このファイルリストを参考にし、各種ファイルをPRAATで開くことが可能です。
