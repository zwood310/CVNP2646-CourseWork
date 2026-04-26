#!/usr/bin/env python3

from pathlib import Path #pathlib module for easier time iterating over files
from datetime import datetime
import  glob, json, shutil

#Intro: Prompt user for path to be scanned
hellomsg=("Hello, please enter directory to be scanned:")
print(f"{hellomsg}")
scanpath=input() #user chooses path

pdir = Path(scanpath) #sets user chosen path as variable 'pdir'
print(f"Scanning {pdir}...") #prints path to screen, lets user know scan will begin

#counts for json report
file_counts = {"documents": 0, "images": 0, "executables": 0, "archives": 0, "videos": 0, "audio": 0, "other": 0}
total_files = [0] #wouldn't work as integer... made into list then converted to integer after counts were updated

# defining the extension categories
documents = ["*.pdf", "*.doc", "*.docx", "*.txt", "*.rtf", "*.odt"]
images = ["*.png", "*.jpg", "*.jpeg", "*.gif", "*.bmp", "*.svg", "*.webp"]
executables = ["*.exe", "*.msi", "*.bat", "*.sh", "*.app"]
archives =["*.zip", "*.tar", "*.gz", "*.rar", "*.7z"]
videos = ["*.mp4", "*.mov", "*.avi", "*.mkv", "*.wmv"]
audio = ["*.mp3", "*.wav", "*.flac", "*.aac", "*.ogg"]

def filemover(cat, catlist): #actually moves the files

    newdir = Path(f"{scanpath}/organized_files/{cat}")
    newdir.mkdir(parents=True, exist_ok=True)

    for pattern in catlist:
        for p in glob.glob(f"{scanpath}/{pattern}"): #this is the extension extractor
            file_counts[cat] += 1
            total_files[0] += 1
            shutil.move(p, newdir)

#call all categories
filemover('documents', documents)
filemover('images', images)
filemover('executables', executables)
filemover('archives', archives)
filemover('videos', videos)
filemover('audio', audio)

def filemoverex(): #after files are moved, move leftovers (other files)
    
    newdir = Path(f"{scanpath}/organized_files/other")
    newdir.mkdir(parents=True, exist_ok=True)
    for file in pdir.iterdir():
        if file.is_file():
         file_counts["other"] += 1
         total_files[0] += 1
         shutil.move(file, newdir)

#call other category
filemoverex()

total_integer = int(''.join(map(str, total_files))) #turn total into integer

#json report generation
def json_gen(file_counts, total_integer, scanpath):
   report = {"timestamp": datetime.now().isoformat(), "source_directory": scanpath, "total_files": total_integer, "categories": file_counts, "organized": sum(file_counts.values()) }
   with open("organization_report.json", "w") as f: json.dump(report, f, indent=4)
   return report

json_gen(file_counts, total_integer, scanpath) #call json generator

#convert json to human readable text
def text_gen(file_counts, total_integer):
   report = "FILE ORGANIZATION REPORT\n"
   report += "=" * 40 + "\n\n"
   report += f"Directory Path: {scanpath}\n"
   report += f"Organized on {datetime.now().isoformat()}\n\n"
   report += "=" * 40 + "\n\n"
   report += f"Total Files: {total_integer}\n\n"
   for category, count in file_counts.items():
      percentage = (count / total_integer * 100) if total_integer > 0 else 0
      report += f"{category.upper()}: {count} ({percentage:.1f}%)\n"
   print (report)
   report_location = Path(f"{scanpath}/report.txt")
   report_location.write_text(report) #saves report to text file
   return report

#generate text report
text_gen(file_counts, total_integer)