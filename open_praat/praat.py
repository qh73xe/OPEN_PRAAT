# -*- coding: utf-8 -*
"""praat.py

:DATE: 2019/12/25 17:20:31

PRAAT を使用した関数群一式を記述します。

"""
from pathlib import Path
from time import sleep
import subprocess

from logger import createLogger

SCRIPT_DIR = Path(__file__).parent.joinpath("praat").resolve()
LOGGER = createLogger(__name__)


def praat_run(script_path, *args):
    cmds = ["praat", "--run", str(script_path)]
    if args:
        cmds.extend(args)
    LOGGER.info('PRAAT:RUN: {}'.format(" ".join(cmds)))
    subprocess.call(cmds)


def denoising(wpath, output_path):
    Path(output_path).parent.resolve().mkdir(parents=True, exist_ok=True)
    script_path = SCRIPT_DIR.joinpath("denoising.praat")
    praat_run(script_path, wpath, output_path)


def create_textgrid(wpath, output_path):
    Path(output_path).parent.resolve().mkdir(parents=True, exist_ok=True)
    script_path = SCRIPT_DIR.joinpath("create_textgrid.praat")
    praat_run(script_path, wpath, output_path)


def get_tire_names(tgpath):
    from tgt import read_textgrid
    tg = read_textgrid(tgpath)
    return [t.name for t in tg.tiers]


class Praat(object):

    praat = "praat"
    sendpraat = "sendpraat"
    os_type = "Linux"
    wpath = None
    tgpath = None
    proc = None

    def __set_os(self):
        """OS 毎の設定を決定します"""
        from platform import system
        self.osType = system()
        if self.osType == 'Linux':
            self.praat = 'praat'
            self.sendpraat = 'sendpraat'
        elif self.osType == 'Windows':
            self.praat = 'C:\Program Files\Praat.exe'
            self.sendpraat = 'C:\Program Files\sendpraat.exe'
        elif self.osType == 'Darwin':
            self.praat = '/Applications/Praat.app/Contents/MacOS/Praat'
            self.sendpraat = 'sendpraat_carbon'

    def __init__(self, wpath, tgpath):
        self.wpath = Path(wpath)
        self.tgpath = Path(tgpath)
        self.__set_os()
        if self.proc:
            self.close()

        self.proc = subprocess.Popen(
            [self.praat, "--open", wpath, tgpath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        sleep(2)
        LOGGER.info('PRAAT:PROC:START')

    def send_praat(self, scripts):
        if self.proc:
            LOGGER.info('SENDPRAAT:RUN:\n\t{}'.format('\n\t'.join(scripts)))
            cmds = [self.sendpraat, "100", 'praat']
            if self.osType == 'Darwin':
                scripts = [l.encode('shift-jis') for l in scripts]
            cmds.extend(scripts)
            subprocess.call(cmds)
        else:
            LOGGER.error("PRAAT: PROC is KILLED")

    def view(self, length=5, start=None, end=None):
        if not start:
            start = 0.0
        if not end:
            end = start + length
        self.send_praat(
            [
                'selectObject: "Sound {}"'.format(self.wpath.stem),
                'plusObject: "TextGrid {}"'.format(self.tgpath.stem),
                'fileName$ = selected$("TextGrid")',
                'textGridObjName$ = "TextGrid " + fileName$',
                'View & Edit',
                "editor TextGrid 'fileName$'",
                'Zoom: {}, {}'.format(start, end),
                'endeditor',
            ]
        )

    def addWord(self, tier, word, channel=None):
        """現在の選択範囲に `word` を挿入します."""
        select_tier_cmd = self._get_select_tier_cmd(tier, channel=channel)
        current_info_cmd = self._get_selected_interval_cmd()
        self.send_praat(
            [
                *current_info_cmd, *select_tier_cmd,
                'strBoundaryID = {}: layer, selectedStrTime'.
                format('Get interval boundary from time'),
                'label$ = Get label of interval: layer, strBoundaryID',
                'label$ = label$ + "{}"'.format(word),
                'Set interval text: layer, strBoundaryID, label$'
            ]
        )

    def addBoundaly(self, tier, word, **kwargs):
        """IntervalTier に Boundary を挿入します.

        Args:
            tier : 操作対象の tier 名
            word : 挿入する文字列
            channel (str, optional) : 音声チャンネル['R' | 'L'].
                存在しない場合には None になります. default = None.
            limit (flot, optional) : 前のインターバルとの最低限の距離.
                存在しない場合, 0 になります. default = 0.
            notSoundingText (str, optional) : 非音声区間テキスト.
                挿入したバウンダリーの後ろの文字. default = ''.
        """
        channel = kwargs.get('channel', None)
        notSoundingText = kwargs.get('notSoundingText', "#")
        strat_time = kwargs.get('strat_time', 'selectedStrTime')
        end_time = kwargs.get('end_time', 'selectedEndTime')

        select_tier_cmd = self._get_select_tier_cmd(tier, channel=channel)
        current_info_cmd = self._get_selected_interval_cmd()

        if notSoundingText:
            set_word = [
                'Set interval text: layer, strBoundaryID, "{}"'.format(word),
                'Set interval text: layer, {}, "{}"'.format(
                    'nextBoundaryID', notSoundingText
                )
            ]
        else:
            set_word = [
                'Set interval text: layer, strBoundaryID, "{}"'.format(word),
            ]
        self.send_praat(
            [
                *current_info_cmd,
                *select_tier_cmd,
                # バウンダリーの挿入
                'Insert boundary: layer, {}'.format(strat_time),
                'Insert boundary: layer, {}'.format(end_time),
                # 挿入したバウンダリーの 固有ID の取得
                'strBoundaryID = {}: layer, {}'.format(
                    'Get interval boundary from time', strat_time
                ),
                'endBoundaryID = {}: layer, {}'.format(
                    'Get interval boundary from time', end_time
                ),
                'nextBoundaryID = strBoundaryID + 1',
                *set_word,
            ]
        )

    def removeBoundaly(self, tier, channel=None):
        select_tier_cmd = self._get_select_tier_cmd(tier, channel=channel)
        current_info_cmd = self._get_selected_interval_cmd()
        self.send_praat(
            [
                *current_info_cmd, *select_tier_cmd,
                'strBoundaryID = {}: layer, selectedStrTime'.
                format('Get interval boundary from time'),
                'nextBoundaryID = strBoundaryID + 1',
                'tergetID = strBoundaryID - 1',
                'label$ = Get label of interval: layer, tergetID',
                'Remove right boundary: layer, strBoundaryID',
                'Remove left boundary: layer, strBoundaryID',
                'boundaryID = strBoundaryID - 1',
                'Set interval text: layer, boundaryID, label$'
            ]
        )

    def saveTextGrid(self):
        self.send_praat(
            [
                'fileName$ = selected$("TextGrid")',
                'textGridObjName$ = "TextGrid " + fileName$',
                'selectObject: textGridObjName$',
                'saveFile$ = fileName$ + ".TextGrid"',
                'Save as text file: "{}"'.format(self.tgpath)
            ]
        )
        LOGGER.info("SAVE: TEXTGRID".format(self.tgpath))

    def close(self):
        if self.proc:
            self.saveTextGrid()
            sleep(1)
            self.proc.kill()
            LOGGER.info('PRAAT:PROC:KILLED')
            sleep(1)

    def _get_selected_interval_cmd(self):
        """praat editor 上で現在選択されている時間情報を取得するコマンドを返しま
        す。

        このコマンドを事前に実施することで、以後のPRAAT SCRIPT 上では以下の変数
        が使用可能になります。

        preLvelStrTime: 一つ前のインターバル開始時刻
        selectedStrTime: 現在のインターバル開始時刻
        selectedEndTime: 現在のインターバル修了時刻

        Warning:
            このコマンドは praat scripts 文を
            発行するのみであり, 実行はしないので注意してください.

        """
        return [
            'fileName$ = selected$("TextGrid")',
            'textGridObjName$ = "TextGrid " + fileName$',
            'selectObject: textGridObjName$', "editor TextGrid 'fileName$'",
            'preLvelStrTime = Get starting point of interval',
            'selectedStrTime = Get start of selection',
            'selectedEndTime = Get end of selection', 'endeditor'
        ]

    def _get_select_tier_cmd(self, name, channel=None):
        """特定の Tier を選択させるコマンドを出力します.

        Args:
            name : 選択する Tier 名
            channel : チャンネル名

        Warning:
            このコマンドは特定の Tier を選択する praat scripts 文を
            発行するのみであり, 実行はしないので注意してください.

        """
        if channel == 'R' or channel == 'L':
            name = "{}_{}".format(name, channel)

        return [
            'for i to do("Get number of tiers")',
            'if do$("Get tier name...", i) = "{}"'.format(name),
            'layer = i',
            'endif',
            'endfor',
            'selectObject: textGridObjName$',
        ]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


if __name__ == "__main__":
    origin = "/home/qh73xe/Documents/corpora/realTimeMRI/20171225/Asai/WAV_R/1001/split/5.WAV"
    denoised = "/home/qh73xe/Documents/corpora/realTimeMRI/20171225/Asai/WAV_R/1001/SS/5.WAV"
    textGrid = "/home/qh73xe/Documents/corpora/realTimeMRI/20171225/Asai/TextGrid/5.TextGrid"
    denoising(origin, denoised)
    create_textgrid(denoised, textGrid)

    praat = Praat(denoised, textGrid)
    praat.view()
