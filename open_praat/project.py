# -*- coding: utf-8 -*
"""open_praat/project.py

:DATE: 2019/12/25 20:16:16

アノテーション実施時の作業コマンド。
このコマンド群は充分に抽象化していないので注意してください。


Example:
    プロジェクトファイルを作成するには以下のようにします::

        python project.py -p <project_name> -w <wavdir>

    なお、 <wavdir> にはワイルドカードが使用可能です。

"""
import json
from pathlib import Path

from praat import denoising, create_textgrid
from logger import createLogger

CONFDIR = Path.home().joinpath(".config", "open-praat", "projects")
LOGGER = createLogger(__name__)


def init_project(project_name, wdir):
    from glob import glob
    from os import path
    LOGGER.info("INIT_PROJECT: {}, {}".format(project_name, wdir))
    projectdir = CONFDIR.joinpath(project_name)
    Path(projectdir).mkdir(parents=True, exist_ok=True)

    wavs = glob(path.join(path.expanduser(wdir), "*.WAV"))
    items = []
    for w in wavs:
        woutdir = path.join(path.dirname(path.dirname(w)), "SS")
        tgoutdir = path.join(path.dirname(path.dirname(w)), "TextGrid")

        out_wpath = path.join(woutdir, path.basename(w))
        out_tgpath = path.join(
            tgoutdir, "{}.TextGrid".format(path.splitext(path.basename(w))[0])
        )
        if not Path(out_wpath).exists():
            denoising(w, out_wpath)
        if not Path(out_tgpath).exists():
            create_textgrid(out_wpath, out_tgpath)
        items.append({"wav": out_wpath, "tg": out_tgpath})

    with open(str(projectdir.joinpath("filelist.json")), 'w') as f:
        json.dump({"files": items}, f, indent=4)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", '--project', help='プロジェクト名', type=str, required=True
    )
    parser.add_argument(
        "-w", '--wavdir', help='解析対象ディレクトリ', type=str, required=True
    )
    args = parser.parse_args()
    init_project(args.project, args.wavdir)
