import os 
import xml.etree.ElementTree
import requests
from bs4 import BeautifulSoup
import json
import progressbar
import time
import sys

cwd = os.getcwd()

def read_net_nugets():
	p = []
	path = cwd + "\\Client\\packages.config"
	e = xml.etree.ElementTree.parse(path).getroot()
	for atype in e.findall('package'):
		p.append(atype.get('id'))
	return p
	
def read_core_nugets():	
	p = []
	for f in ["Shared", "Server"]:
		path = cwd + "\\" + f + "\\" + f + ".csproj"
		e = xml.etree.ElementTree.parse(path).getroot()	
		
		for atype in e.findall('ItemGroup'):
			for btype in atype.findall('PackageReference'):
				p.append(btype.get('Include'))
	return p

def GetHTTPData(package):
	r = requests.get('https://api-v2v3search-0.nuget.org/query?q=' + package)
	j = json.loads(r.content)
	for d in j["data"]:
		time.sleep(0.1)
		if(d["id"] == package):
			licenseUrl = ""
			projectUrl = ""
			title = ""
			if("licenseUrl" in d):			
				licenseUrl = d["licenseUrl"]
			if("projectUrl" in d):
				projectUrl = d["projectUrl"]
			if("title" in d):
				title = d["title"]
			
			return (title, projectUrl, licenseUrl)
	
	
def main():	
	packages = []
	packages += read_net_nugets()
	packages += read_core_nugets()
	packages = list(set(packages))
	
	ldata = []
		
	with progressbar.ProgressBar(max_value=len(packages)) as bar:
		for i,p in enumerate(packages):
			ldata.append(GetHTTPData(p))
			bar.update(i)
				
	ldata = sorted(ldata, key=lambda tup: tup[1])	
	
	
	with open("Nuget_LICENSES.md", 'w') as f:
		i = 0
		f.write("### Licenses of nugets\n")
		for p in ldata:
			if(len(p[1]) > 0):
				if(len(p[2]) > 0):
					f.write(" - [" + p[0] + "][" + str(i) + "] [License][" + str(i+1) + "]\n")
					i += 2			
				else:
					f.write(" - [" + p[0] + "][" + str(i) + "] \n")
					i += 1
			else:
				if(len(p[2]) > 0):
					f.write(" - " + p[0] + " [License][" + str(i) + "]\n")
					i += 1				
				else:
					f.write(" - " + p[0] + "\n")
				

		f.write("\n")
		
		i = 0
		
		for p in ldata:
			if(len(p[1]) > 0):
				f.write("[" + str(i) + "]: " + p[1] + "\n")
				i += 1
			if(len(p[2]) > 0):
				f.write("[" + str(i) + "]: " + p[2] + "\n")
				i += 1
	
		
if __name__ == "__main__":
    main()
