import json
import os


class Utils(object):
    def getFileDict(self, file_path):
        '''
        @returns <dict> dict[hotkey]=file_path
        '''
        if file_path:
            with open(file_path, 'r') as f:
                hotkeys = json.load(f)
                return hotkeys
                # for key in list(hotkeys.keys()):
                #     hotkeys[key] = str(hotkeys[key])
                # return hotkeys

    def checkFileType(self, file_path):
        '''
        @file_path <str> path on disk to file
        '''
        if os.path.exists(file_path):
            if os.path.isdir(file_path):
                return 'group'
            elif file_path.endswith('.py'):
                return 'script'
            elif file_path.endswith('.json'):
                if file_path:
                    with open(file_path, 'r') as f:
                        hotkeys = json.load(f)
                        if len(list(hotkeys.keys())) == 16:
                            return 'hotkey'
                        elif len(list(hotkeys.keys())) == 8:
                            return 'gesture'



