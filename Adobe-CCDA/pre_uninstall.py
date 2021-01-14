#!/usr/local/munki/munki-python

## Author: Jacob Burley <github-contact@jc0b.computer>

import glob

ADOBE_UNINSTALL_DIR = '/Library/Application Support/Adobe/Uninstall/'

SAP_CODES = {
	'after_effects': 'AEFT',
	'animate': 'FLPR',
	'audition': 'AUDT',
	'bridge': 'KBRG',
	'character_animator': 'CHAR',
	'dimension': 'ESHR',
	'dreamweaver': 'DRWV',
	'illustrator': 'ILST',
	'incopy': 'AICY',
	'indesign': 'IDSN',
	'lightroom': 'LRCC',
	'lightroom_classic': 'LTRM',
	'media_encoder': 'AME',
	'photoshop': 'PHSP',
	'prelude': 'PRLD',
	'premiere_pro': 'PPRO',
	'premiere_rush': 'RUSH',
	'substance_alchemist': 'SBSTA',
	'substance_designer': 'SBSTD',
	'substance_painter': 'SBSTP',
	'xd': 'SPRK'
}

def search(sap_code):
	for code in SAP_CODES: 
		if sap_code == SAP_CODES[code]:
			return True
	return False

def parse(application):
	application = application.replace(ADOBE_UNINSTALL_DIR, '')
	application = application.replace('.app', '')
	application = application.split('_')
	version = '.'.join(application[1:])
	app_tuple = (application[0], version)
	return app_tuple


def main():
	apps = glob.glob(ADOBE_UNINSTALL_DIR + '*.app')
	uninstall_array = []
	for app in apps:
		app_info = parse(app)
		if(search(app_info[0])):
			uninstall_array.append(app_info)
	if(len(uninstall_array) > 0):
		print("The following items still need to be uninstalled before CCDA can be removed:")
		for app in uninstall_array:
			print(app[0])
		exit(1)
	elif(len(uninstall_array) == 0):
		print("No Adobe apps installed. CCDA can be removed.")
		exit(0)
		
if __name__ == '__main__':
	main()