import maya.cmds as cmds
import os
import subprocess
import configparser

# iniファイルのパス
config_file_path = os.path.join(os.path.expanduser('~'), 'Documents', 'maya', '2025', 'scripts', 'Folder_List_Tool', 'user_path_data_list' , 'user_path_data_list.ini')

# フォルダのパスを取得
folder_path = os.path.dirname(config_file_path)

# フォルダが存在しない場合、新たにフォルダを作成
if not os.path.exists(folder_path):
    os.makedirs(folder_path)
    print(f"フォルダ '{folder_path}' を作成しました。")

# 選択されたフォルダのパスを格納するリスト
folder_list = []

# iniファイルを読み込む
def load_folder_list_from_ini():
    folder_list.clear()  # リストをクリアしてから読み込む
    config = configparser.ConfigParser()
    if os.path.exists(config_file_path):
        config.read(config_file_path)
        if 'Folders' in config and 'folder_paths' in config['Folders']:
            folder_paths = config['Folders']['folder_paths'].split(',')
            folder_list.extend(folder_paths)
            print("iniファイルからフォルダリストを読み込みました")

# フォルダリストをiniファイルに保存
def save_folder_list_to_ini():
    config = configparser.ConfigParser()
    config['Folders'] = {'folder_paths': ','.join(folder_list)}
    with open(config_file_path, 'w') as configfile:
        config.write(configfile)
    print(f"フォルダリストパスをiniファイルに保存しました: {config_file_path}")


# リストに選択追加(ダイアログを表示)|ここから
def select_folder():
    # フォルダ選択ダイアログを表示
    folder_path = cmds.fileDialog2(fileMode=3, dialogStyle=2, caption="フォルダを選択")

    # 選択したパスを返す（リストで返ってくるので最初の要素を取得）
    if folder_path:
        folder_path_win = folder_path[0].replace('/', '\\')
        return folder_path_win
    else:
        #cmds.warning("フォルダが選択されませんでした")
        return None

# リストに選択追加
def add_folder_to_list():
    selected_folder = select_folder()

    if selected_folder:
        if selected_folder not in folder_list:  # 重複チェック
            folder_list.append(selected_folder)
            print(f"フォルダがリストに追加されました: {selected_folder}")
            refresh_folder_list()
            save_folder_list_to_ini()  # フォルダリストをiniファイルに保存
        else:
            print(f"フォルダは既にリストに存在します: {selected_folder}")
    else:
        cmds.warning("フォルダが選択されませんでした")

#|ここまで

# リストに手動入力
def add_folder_manually_to_list():
    result = cmds.promptDialog(
        title='フォルダパスの手動入力',
        message='フォルダパスを入力してください:',
        button=['OK', 'キャンセル'],
        defaultButton='OK',
        cancelButton='キャンセル',
        dismissString='キャンセル'
    )

    if result == 'OK':
        folder_path = cmds.promptDialog(query=True, text=True)
        if folder_path:
            if folder_path not in folder_list:  # 重複チェック
                folder_list.append(folder_path)
                print(f"フォルダが手動でリストに追加されました: {folder_path}")
                refresh_folder_list()
                save_folder_list_to_ini()  # フォルダリストをiniファイルに保存
            else:
                print(f"フォルダは既にリストに存在します: {folder_path}")
        else:
            print("フォルダパスが入力されませんでした")

def remove_selected_folder():
    # 現在選択されているリスト項目を取得
    selected_items = cmds.textScrollList('folderListWidget', query=True, selectItem=True)
    if selected_items:
        selected_folder = selected_items[0]
        # リストから削除
        if selected_folder in folder_list:
            folder_list.remove(selected_folder)
            print(f"フォルダがリストから削除されました: {selected_folder}")
            refresh_folder_list()
            save_folder_list_to_ini()  # フォルダリストを更新してiniファイルに保存
    else:
        print("削除するフォルダが選択されていません")

def open_folder_in_explorer():
    # 現在選択されているリスト項目を取得
    selected_items = cmds.textScrollList('folderListWidget', query=True, selectItem=True)
    if selected_items:
        selected_folder = selected_items[0]

        if os.path.exists(selected_folder):
            # Windowsの場合はexplorerを使用し、macOSの場合はopenコマンドを使用
            if os.name == 'nt':  # Windows
                subprocess.Popen(['explorer', selected_folder])
            elif os.name == 'posix':  # macOS
                subprocess.Popen(['open', selected_folder])
            else:  # サポートされていないOS
                print("ファイルエクスプローラーを開くにはサポートされていないOSです")
            print(f"選択されたファイルパス: {selected_folder}")
        else:
            print(f"フォルダが存在しません: {selected_folder}")
            cmds.warning(f"フォルダが存在しません: {selected_folder}")
    else:
        print("エクスプローラーで開くフォルダが選択されていません")

# シーンパスを取得
def get_scene_path():
    scene_path = cmds.file(query=True, sceneName=True)
    if scene_path:
        return scene_path
    else:
        return "シーンが保存されていません"

# シーンのフォルダパスを取得
def get_scene_folder_path():
    file_path = get_scene_path()
    if "シーンが保存されていません" not in file_path:
        folder_path = os.path.dirname(file_path).replace('/', '\\')
        return folder_path
    else:
        return file_path

# シーンフォルダをエクスプローラーで開く
def open_scene_folder_in_explorer(*args):
    folder_path = get_scene_folder_path()
    if "シーンが保存されていません" not in folder_path:
        if os.name == 'nt':  # Windows
            subprocess.Popen(f'explorer "{folder_path}"')
            print(f"シーンフォルダのパス: {folder_path}")
        elif os.name == 'posix':  # macOS
            subprocess.Popen(['open', folder_path])
            print(f"シーンフォルダのパス: {folder_path}")
        else:
            cmds.warning("ファイルエクスプローラーを開くにはサポートされていないOSです")
    else:
        cmds.warning("シーンが保存されていません シーンを保存してください")

# sourceimagesフォルダのパスを取得
def get_sourceimages_path():
    project_path = cmds.workspace(query=True, rootDirectory=True)
    sourceimages_path = cmds.workspace(fileRuleEntry="sourceImages")
    full_sourceimages_path = os.path.join(project_path, sourceimages_path)

    if os.path.exists(full_sourceimages_path):
        return full_sourceimages_path
    else:
        return "ソースフォルダが見つかりません"

# フォルダパスを取得
def get_sourceimages_folder_path():
    full_sourceimages_path = get_sourceimages_path()
    if "ソースフォルダが見つかりません" not in full_sourceimages_path:
        folder_sourceimages_path = full_sourceimages_path.replace('/', '\\')
        return folder_sourceimages_path
    else:
        return full_sourceimages_path

# sourceimagesフォルダをエクスプローラーで開く
def open_sourceimages_folder_in_explorer(*args):
    folder_sourceimages_path = get_sourceimages_folder_path()
    if "ソースイメージフォルダが見つかりません" not in folder_sourceimages_path:
        if os.name == 'nt':  # Windows
            subprocess.Popen(f'explorer "{folder_sourceimages_path}"')
            print(f"ソースイメージフォルダのパス: {folder_sourceimages_path}")
        elif os.name == 'posix':  # macOS
            subprocess.Popen(['open', folder_sourceimages_path])
            print(f"ソースイメージフォルダのパス: {folder_sourceimages_path}")
        else:
            cmds.warning("ファイルエクスプローラーを開くのにサポートされていないOSです")
    else:
        cmds.warning("ソースイメージフォルダが見つかりません")


# 作業フォルダを作成する("fbx", "obj", "psd", "reference", "ssp", "zb")
# sourceimagesフォルダのパスを取得
def get_sourceimages_path():
    project_path = cmds.workspace(query=True, rootDirectory=True)
    sourceimages_path = cmds.workspace(fileRuleEntry="sourceImages")
    full_sourceimages_path = os.path.join(project_path, sourceimages_path)

    if os.path.exists(full_sourceimages_path):
        return full_sourceimages_path.replace('/', '\\')  # Windows形式に変換
    else:
        cmds.warning("sourceimagesフォルダが見つかりません")
        return None

# sourceimagesフォルダからユーザーがフォルダを選択
def select_folder_in_sourceimages():
    sourceimages_path = get_sourceimages_path()
    if not sourceimages_path:
        return None

    # cmds.fileDialog2を使用してフォルダを選択
    selected_folder = cmds.fileDialog2(
        dialogStyle=2,  # モーダルスタイルのダイアログ
        fileMode=3,     # フォルダ選択モード
        startingDirectory=sourceimages_path,  # sourceimagesフォルダを初期パスに設定
        caption="フォルダを選択"
    )

    if selected_folder:
        selected_folder_path = selected_folder[0].replace('/', '\\')  # Windows形式に変換
        print(f"選択されたフォルダ: {selected_folder_path}")
        return selected_folder_path
    else:
        cmds.warning("フォルダが選択されませんでした")
        return None

# フォルダを作成する関数
def create_folders_in_selected_folder():
    folder_path = select_folder_in_sourceimages()

    if not folder_path:
        return

    folder_names = ["fbx", "obj", "psd", "reference", "ssp", "zb"]
    created_folders = []  # 作成されたフォルダを格納

    for folder in folder_names:
        full_path = os.path.join(folder_path, folder).replace('/', '\\')  # Windows形式に変換
        if not os.path.exists(full_path):
            os.makedirs(full_path)
            print(f"フォルダ作成されました: {full_path}")
            created_folders.append(full_path)
        else:
            print(f"すでにフォルダが存在しています: {full_path}")

# リストに追加
    added_folders = created_folders  # リストで取得

    print(f"格納されたリスト{added_folders}")

    if added_folders:
        for folder in added_folders:
            if folder not in folder_list:  # 重複チェック
                folder_list.append(folder)
                print(f"フォルダがリストに追加されました: {folder}")
            else:
                print(f"フォルダは既にリストに存在します: {folder}")

        refresh_folder_list()  # フォルダリストをUIに反映
        save_folder_list_to_ini()  # iniファイルに保存
    else:
        cmds.warning("既にフォルダが存在しています")


# ワークスペースのパスを取得
def get_workspace_path():
    project_path = cmds.workspace(query=True, rootDirectory=True)
    project_path_win = project_path.replace('/', '\\')
    return project_path_win

# ワークスペースをエクスプローラーで開く
def open_workspace_in_explorer(*args):
    workspace_path = get_workspace_path()
    if os.path.exists(workspace_path):
        if os.name == 'nt':  # Windows
            subprocess.Popen(f'explorer "{workspace_path}"')
            print(f"ワークスペースのパス: {workspace_path}")
        elif os.name == 'posix':  # macOS
            subprocess.Popen(['open', workspace_path])
            print(f"ワークスペースのパス: {workspace_path}")
        else:
            cmds.warning("ファイルエクスプローラーを開くのにサポートされていないOSです")
    else:
        cmds.warning("ワークスペースが見つかりません")


# #iniファイルを開く
def open_ini_folder_in_explorer(*args):
    folder_ini_path = config_file_path
    if "iniファイルが見つかりません" not in folder_ini_path:
        if os.name == 'nt':  # Windows
            subprocess.Popen(f'explorer "{folder_ini_path}"')
        elif os.name == 'posix':  # macOS
            subprocess.Popen(['open', folder_ini_path])
        else:
            cmds.warning("ファイルエクスプローラーを開くのにサポートされていないOSです")
    else:
        cmds.warning("iniファイルが見つかりません")

def clear_folder_list():
    """リストを全てクリアして、保存する"""
    folder_list.clear()  # リストをクリア
    print("フォルダリストがクリアされました")
    refresh_folder_list()  # UI上のリストを更新
    save_folder_list_to_ini()  # クリアされた状態をiniファイルに保存

# ライセンス表示
def show_license(*args):
    # ダイアログウィンドウが既に存在する場合は削除
    if cmds.window('license', exists=True):
        cmds.deleteUI('license')

    # ダイアログウィンドウを作成
    cmds.window('license', title="MIT License", widthHeight=(480, 370))
    cmds.columnLayout(adjustableColumn=True)

    # MIT Licenseの内容を表示
    license_text = (
        "MIT License\n\n"
        "Copyright (c) 2024 Naruse\n\n"
        "Permission is hereby granted, free of charge, to any person obtaining a copy\n"
        "of this software and associated documentation files (the \"Software\"), to deal\n"
        "in the Software without restriction, including without limitation the rights\n"
        "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n"
        "copies of the Software, and to permit persons to whom the Software is\n"
        "furnished to do so, subject to the following conditions:\n\n"
        "The above copyright notice and this permission notice shall be included in all\n"
        "copies or substantial portions of the Software.\n\n"
        "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n"
        "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n"
        "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n"
        "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n"
        "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n"
        "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n"
        "SOFTWARE."
    )

    cmds.text(label=license_text, align='left', wordWrap=True, height=330)

    # OKボタンを作成し、ダイアログを閉じる
    cmds.separator(height=10, style='none') #隙間
    cmds.button(label="OK", command=lambda x: cmds.deleteUI('license'))

    cmds.showWindow('license')

def refresh_folder_list():
    # フォルダリストをリフレッシュして表示
    cmds.textScrollList('folderListWidget', edit=True, removeAll=True)  # リストをクリア
    for folder in folder_list:
        cmds.textScrollList('folderListWidget', edit=True, append=folder)  # フォルダを追加

# ここからUI

def create_ui():
    if cmds.window('folderWindow', exists=True):
        cmds.deleteUI('folderWindow')

    # ウィンドウ作成
    window = cmds.window('folderWindow', title="Folder List Tool", widthHeight=(400, 600))
    cmds.columnLayout(adjustableColumn=True)

    # フォルダリスト表示のためのTextScrollList
    cmds.textScrollList('folderListWidget', numberOfRows=14, height=200, allowMultiSelection=False)

    cmds.separator(height=10, style='in') #仕切り

    # フォルダを追加するボタン
    cmds.button(label="フォルダパスを追加", command=lambda x: add_folder_to_list())

    cmds.separator(height=3, style='none')  # 隙間

    # フォルダパスを手動で追加するボタン
    cmds.button(label="フォルダパスを手動で追加", command=lambda x: add_folder_manually_to_list())

    cmds.separator(height=3, style='none')  # 隙間

    # 選択されたフォルダを削除するボタン
    cmds.button(label="選択したフォルダパスを削除", command=lambda x: remove_selected_folder())

    cmds.separator(height=3, style='none')  # 隙間

    # リストを全てクリアするボタン
    cmds.button(label="リストを全てクリア", command=lambda x: clear_folder_list())

    cmds.separator(height=15, style='in') #仕切り

    # 選択されたフォルダをエクスプローラーで開くボタン
    cmds.button(label="選択したパスをエクスプローラーで開く", command=lambda x: open_folder_in_explorer())

    cmds.separator(height=15, style='in') #仕切り

    # おまけ
    cmds.frameLayout(label="おまけ", collapsable=True, collapse=True, width=300)
    cmds.columnLayout(adjustableColumn=True)
    cmds.separator(height=5, style='none') #隙間

    # 作業フォルダ作成
    cmds.button(label="作業フォルダを作成", command=lambda _: create_folders_in_selected_folder())

    cmds.separator(height=3, style='none') #隙間

    cmds.button(label="シーンフォルダを開く", command=open_scene_folder_in_explorer)

    cmds.separator(height=3, style='none')  # 隙間

    cmds.button(label="ソースイメージフォルダを開く", command=open_sourceimages_folder_in_explorer)

    cmds.separator(height=3, style='none')  # 隙間

    cmds.button(label="ワークスペースフォルダを開く", command=open_workspace_in_explorer)

    cmds.separator(height=3, style='none')  # 隙間

    #iniファイルを開く
    cmds.button(label="iniファイルを開く", command=open_ini_folder_in_explorer)
    cmds.setParent('..')
    cmds.setParent('..')

    cmds.separator(height=3, style='none')  # 隙間

    # About
    cmds.frameLayout(label="About", collapsable=True, collapse=True, width=300)
    cmds.columnLayout(adjustableColumn=True)
    cmds.text(label="スクリプト名:Folder List Tool",align='left')
    cmds.text(label="作成者:Naruse, GPT-4o",align='left')
    cmds.text(label="作成日:2024年10月7日",align='left')
    cmds.text(label="更新日:2025年11月24日",align='left')
    cmds.text(label="バージョン:v0.3",align='left')
    cmds.text(label="ライセンス:MIT License",align='left')
    cmds.separator(height=5, style='none')
    # show_license関数を呼び出す
    cmds.button(label="License", command=show_license)
    cmds.setParent('..')
    cmds.setParent('..')

    # 起動時にiniファイルからフォルダリストを読み込み、表示を更新
    load_folder_list_from_ini()
    refresh_folder_list()

    # ウィンドウを表示
    cmds.showWindow(window)

# UIを表示
create_ui()