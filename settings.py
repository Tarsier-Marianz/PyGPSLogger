from storage import StorageDB
import os


class Settings(object):
    def __init__(self):
        self.strg = StorageDB('gps.sqlite')

        fields = {}
        fields['id'] = 'INTEGER PRIMARY KEY AUTOINCREMENT'
        fields['name'] = 'VARCHAR (50)'
        fields['value'] = 'VARCHAR (255)'
        
        #table for authentication
        auths = {}
        auths['id'] = 'INTEGER PRIMARY KEY AUTOINCREMENT'
        auths['username'] = 'VARCHAR (50)'
        auths['password'] = 'VARCHAR (255)'
		
        #table for workspaces
        workspaces = {}
        workspaces['id'] = 'INTEGER PRIMARY KEY AUTOINCREMENT'
        workspaces['name'] = 'VARCHAR (50)'
        workspaces['count'] = 'INTEGER'
        workspaces['details'] = 'VARCHAR (50)'
        workspaces['date_from'] = 'TEXT'
        workspaces['date_to'] = 'TEXT'
        workspaces['company_id'] = 'VARCHAR (50)'
        workspaces['dispatcher_id'] = 'VARCHAR (100)'
        workspaces['status'] = 'VARCHAR (20)'
        workspaces['code'] = 'VARCHAR (255)'
        
        
        self.strg.CreateTable('settings', fields)
        self.strg.CreateTable('auths', auths)
        self.strg.CreateTable('workspaces', workspaces)
        self.InitDefaultSetting()

    def InitDefaultSetting(self):
        ds = os.path.sep #get default directory separator
        self.userhome = os.path.expanduser('~')
        self.desktop = self.userhome + ds + 'Desktop' + ds + 'wfm' + ds

        dict = {
            'is_autosave': True,
            'baud': 4800,           
            'port': 'COM1',         
            'port_label': 'COM1',         
            'port_old': 'COM1', 
        }

        for s, v in dict.items():
            content_val = {}
            content_val['name'] = s
            content_val['value'] = v
            if not self.strg.IsExist('settings', 'name', s):              
                self.strg.InsertParameterized('settings', content_val)

    def SetSettings(self, name, value):
        content_val = {}
        content_val['name'] = name
        content_val['value'] = value
        if self.strg.IsExist('settings', 'name', name):
            self.strg.UpdateParameterized('settings', content_val, "name='" + name + "'")
        else:
            self.strg.InsertParameterized('settings', content_val)

    def GetSetting(self, name):
        try:
            settings = self.strg.GetValue('settings', 'value', "name='" + str(name) + "'")
            if settings.strip() is None or settings.strip() == '':
                return ''
            else:
                return settings
        except:
            return ''
        
    def SetAuth(self, username, password):
        content_val = {}
        content_val['username'] = username
        content_val['password'] = password
        if self.strg.IsExist('auth', 'username', username):
            self.strg.UpdateParameterized('auth', content_val, "username='" + username + "'")
        else:
            self.strg.InsertParameterized('auth', content_val)
            
        self.SetSettings('username',username)
        self.SetSettings('password',password)
   
    def GetAuth(self, username):
        auths = {}
        auths['username'] = self.strg.GetValue('auth', 'username', "username='" + str(username) + "'")
        auths['password'] = self.strg.GetValue('auth', 'password', "username='" + str(username) + "'")

        return auths