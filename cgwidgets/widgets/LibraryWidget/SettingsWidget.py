import os

"""
convert Settings to JSON
update all widgets to use the JSON
    - add a utils... getSettings() or something like that
read/write json

StyleSheets are now a list... need to be reconcatenated with a ';'.join(stylesheet)
"""

settings_dir = os.environ['HOME'] + '.library'
settings_loc = settings_dir + '/settings.json'


print (os.path.isdir(settings_dir))

#print (settings_location )