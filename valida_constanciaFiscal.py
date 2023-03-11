# Requires Python 3.6 or higher due to f-strings

# Import libraries
import platform
import os
import time
from tempfile import TemporaryDirectory
from pathlib import Path
import sys

import pytesseract
from pdf2image import convert_from_path
import cv2
import validators
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from subprocess import CREATE_NO_WINDOW

from imutils.contours import sort_contours
import multiprocessing
import requests
import zipfile
import configparser
import colorama
from tqdm import tqdm
from collections import namedtuple
import logging
from logging.handlers import RotatingFileHandler

regexRFC = '[A-ZÑ&]{3,4}[0-9]{2}(0[1-9]|1[0-2])(0[1-9]|1[0-9]|2[0-9]|3[0-1])(?:[A-Z\d]{3})'

NUM_THREADS = os.cpu_count()

if platform.system() == "Windows":
	
	out_directory = os.path.abspath(os.getcwd())
	config = configparser.ConfigParser()
	config.read("config.ini")
	path_tesseract = config.get("rutas","ruta_tesseract")
	path_poppler = config.get("rutas","ruta_poppler")
	text_find_file_to_compare = config.get("config","texto_buscar_archivo_a_comparar")
	pytesseract.pytesseract.tesseract_cmd = (out_directory / Path(path_tesseract))
	path_to_poppler_exe = out_directory / Path("poppler")
	chromedriver = out_directory / Path("webdriver/") / "chromedriver.exe"
	edgedriver = out_directory / Path("webdriver/") / "edgedriver.exe"
	
	
else:
	out_directory = Path("~").expanduser()	

dir_path = out_directory / Path("files/")

def main():
	try:	
		colorama.init()
		listFiles = []
		FilesInfoDto = namedtuple("FilesInfoDto", ["name","folder","path"])
		pool = multiprocessing.Pool(NUM_THREADS)
		
		#logging.basicConfig(level=logging.INFO)
		#logger = logging.getLogger(__name__)
		logger = logging.getLogger('registro')
		logger.setLevel(logging.DEBUG)
		handler = RotatingFileHandler('log.txt',mode="a", maxBytes=1024,backupCount=5)
		handler.setLevel(logging.INFO)
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - (%(lineno)d) - %(message)s')
		handler.setFormatter(formatter)
		logger.addHandler(handler)
		
		with TemporaryDirectory() as tempdir:
		# Create a temporary directory to hold our temporary images.

			for nameFolder in os.listdir(dir_path):
				#print(f' Nombre de folder ---> {nameFolder}');
				files_path = dir_path / Path(nameFolder)
				#path_name_folder, base_path_ocr_folder = os.path.split(files_path)
				
				for PDF_file in files_path.iterdir():
					
					if PDF_file.suffix != ".pdf":
						continue
					
					if not text_find_file_to_compare.upper() in PDF_file.stem.upper():
						continue
					
					#print(f'archivo encontrado {PDF_file}')
					start_time = time.time()
					
					''' Main execution point of the program'''
					"""
					Part #1 : Converting PDF to images
					"""
					if platform.system() == "Windows":
						pdf_pages = convert_from_path(
							PDF_file, 500, poppler_path=path_to_poppler_exe, thread_count=NUM_THREADS)
					else:
						pdf_pages = convert_from_path(PDF_file, dpi=500, thread_count=NUM_THREADS)
					# Read in the PDF file at 500 DPI
					
					# Iterate through all the pages stored above
					for page_enumeration, page in enumerate(pdf_pages, start=1):
						# Create a file name to store the image
						filename = f"{tempdir}\page_{page_enumeration:03}.jpg"
						# Save the image of the page in system
						#if not os.path.exists(filename):
						page.save(filename, "JPEG")
						listFiles.append(FilesInfoDto(PDF_file,nameFolder,filename))
						#print(f'imagen guardada en la lista -> {PDF_file} {nameFolder}  {filename}' )
						break
			
			print('procesando...')
			logger.info('procesando...')
			"""
			Part #2 - Recognizing text from the images using OCR
			"""	
			results=[]
			
			with tqdm(total=len(listFiles), dynamic_ncols=True) as pbar:
				isSameFolder= ''
				for infoList in listFiles:
					msg= f"Validando carpeta-> {infoList[1]}"
					message = f'\033[33m{msg}\033[0m'
					if isSameFolder != infoList[1]:
						isSameFolder = infoList[1]
						pbar.write(message)
						logger.info(msg)
					
					result = pool.apply_async(processData,args=(infoList[2],infoList[1],infoList[0],logger))
					result.wait()
					if result.get()=='ok': 
						msg = f'archivo "{infoList[0].stem }{infoList[0].suffix}" - Ok'
						message = f'\033[32m{msg}\033[0m'
						pbar.write(message)
						logger.info(msg)
					else:
						msg = f'archivo "{infoList[0].stem }{infoList[0].suffix}" - Error'
						message = f'\033[31m{msg}\033[0m'
						pbar.write(message)
						logger.info(msg)
						pbar.write(result.get())

					results.append(result)
					pbar.update()
	except Exception as e:
		logger.Exception('Error en el programa')
		
	end_time = time.time()
	print(f"tiempo: {end_time-start_time}")
	logger.info(' **************  finalizado...  **************')
	input("Presiona enter para terminar...")

def sat(line,info_found_sat):
	rfc = "rfc:"
	curp = "curp:"
	nombre = "nombre (s):"
	appellidoPat = "primer apellido:"
	appellidoMat = "segundo apellido:"
				
	if rfc in line.lower():
		info_found_sat.append(line.lower().replace(rfc,"").strip().upper())
	if curp in line.lower():
		info_found_sat.append(line.lower().replace(curp,"").strip().upper())
	if nombre in line.lower():
		info_found_sat.append(line.lower().replace(nombre,"").strip().upper())
	if appellidoPat in line.lower():
		info_found_sat.append(line.lower().replace(appellidoPat,"").strip().upper())
	if appellidoMat in line.lower():
		info_found_sat.append(line.lower().replace(appellidoMat,"").strip().upper())


def processData(image_file,nameFolder,nameFile,logger):
	result = 'error'
	information_list = []
	info_found_sat = []
	webDriver=getWebdriver(logger)
	result = 'xxx1'
	img = cv2.imread(image_file, cv2.IMREAD_GRAYSCALE)
	confir_ocr = f' --user-patterns \'spa.user-patterns\' --psm 6 --oem 1'
	#https://medium.com/nanonets/a-comprehensive-guide-to-ocr-with-tesseract-opencv-and-python-fd42f69e8ca8
	#text = str(pytesseract.image_to_string(img,lang='spa',config=confir_ocr))
	# Recognize the text as string in image using pytesserct
	
	text = str(pytesseract.image_to_string(img,config=confir_ocr))
	lineas = text.split("\n")
	url=''
	
	try:
		# read QR
		img = cv2.imread(image_file)
		detect = cv2.QRCodeDetector()
		value, points, straight_qrcode = detect.detectAndDecode(img)
		if validators.url(value):
			url = value;
	except:
		result = 'error al leer QR'
		logger.info(result)
	
	if url != '':
		try:
			if webDriver is not None:
				for line in lineas:
					sat(line,info_found_sat)
				webDriver.get(url) # Getting page HTML through request
				#find RFC
				rfc = webDriver.find_elements(By.CLASS_NAME , "ui-li-static")[0].text
				if rfc != "":
					resultRegexRFC = re.search(regexRFC,rfc)
					if resultRegexRFC:
						startIndex,endIndex = resultRegexRFC.span()
						information_list.append(rfc[startIndex:endIndex].upper())
				
				# find Datos de indetificacion
				reviews_selector = webDriver.find_elements(By.CLASS_NAME , "ui-datatable-data")
				for review_selector in reviews_selector:
					review_div = review_selector.find_elements(By.TAG_NAME, "tr")
					for row in review_div:
						col = row.find_elements(By.TAG_NAME, "td")[1] #note: index start from 0, 1 is col 2
						information_list.append(col.text)
					break;
				i=0
				error=0
				#Validar los datos del pdf vs QR
				for x in info_found_sat:
					if i==4:
						break
					
					comparacion = information_list[i].strip() != x.strip()
					if comparacion:
						msg=f'\033[31mNo coincide valor -> {x.strip()} (OCR)  vs  {information_list[i].strip()} (Web)\033[0m'
						logger.error(msg)
						error +=1 
					i+=1
				if error>0:
					result = 'error'
				else:
					result = 'ok'
				webDriver.quit()
		except Exception as e:
			result = 'Error al procesar archivo '
			logger.exception(result)
			if not webDriver is None:
				webDriver.quit()
			
	return result
						

def extract_version_chrome_folder():
    # Check if the Chrome folder exists in the x32 or x64 Program Files folders.
    for i in range(2):
        path = 'C:\\Program Files' + (' (x86)' if i else '') +'\\Google\\Chrome\\Application'
        if os.path.isdir(path):
            paths = [f.path for f in os.scandir(path) if f.is_dir()]
            for path in paths:
                filename = os.path.basename(path)
                pattern = '\d+\.\d+\.\d+\.\d+'
                match = re.search(pattern, filename)
                if match and match.group():
                    # Found a Chrome version.
                    return match.group(0)

    return None	
	
def extract_version_edge_folder():
	# Check if the Edge folder exists in the x32 or x64 Program Files folders.
	for i in range(2):
		path = 'C:\\Program Files' + (' (x86)' if i else '') +'\\Microsoft\\Edge\\Application'
		if os.path.isdir(path):
			paths = [f.path for f in os.scandir(path) if f.is_dir()]
			for path in paths:
				filename = os.path.basename(path)
				pattern = '\d+\.\d+\.\d+\.\d+'
				match = re.search(pattern, filename)
				if match and match.group():
					# Found a Edge version.
					return match.group(0)

	return None	


def getWebdriver(logger):
	webDriver= getWebdriverChrome(logger);
	if webDriver is None:
		webDriver= getWebdriverEdge(logger);
	return webDriver


def getWebdriverChrome(logger):
	try:
		# Obtener la versión del navegador Chrome instalado en el sistema
		chrome_version = extract_version_chrome_folder()

		# URL base para descargar el archivo ZIP de Chromedriver
		base_url = 'https://chromedriver.storage.googleapis.com/{}/chromedriver_win32.zip'

		# URL de descarga para el número de versión específico de Chromedriver
		download_url = base_url.format(chrome_version)

		# Descargar el archivo ZIP de Chromedriver
		response = requests.get(download_url)
		
		with open('chromedriver_win32.zip', 'wb') as f:
			f.write(response.content)

		# Descomprimir el archivo ZIP y mover el archivo Chromedriver a la ruta adecuada
		with zipfile.ZipFile('chromedriver_win32.zip', 'r') as zip_ref:
			zip_ref.extractall()
		os.replace('chromedriver.exe', chromedriver)
		
		option_chrome = webdriver.ChromeOptions()
		option_chrome.add_argument('--headless')
		option_chrome.add_argument('--no-sandbox')
		option_chrome.add_argument('--disable-dev-sh-usage')
		option_chrome.add_argument('--disable-gpu')
		option_chrome.add_argument("--disable-extensions")
		option_chrome.add_argument("--log-level=3")
		option_chrome.add_experimental_option('excludeSwitches', ['enable-logging']);
		
		service = Service(executable_path=chromedriver)
		service.creationflags = CREATE_NO_WINDOW
		
		return  webdriver.Chrome(service=service, options=option_chrome)
	except Exception as e:
		result = '--- error al instanciar webdriver para Chrome---'
		logger.info(f'Exception: {result}')
		return
		
def getWebdriverEdge(logger):
	try:
		# Obtener la versión del navegador edge instalado en el sistema
		edge_version = extract_version_edge_folder()

		# URL base para descargar el archivo ZIP de Edgedriver
		base_url = 'https://msedgedriver.azureedge.net/{}/edgedriver_win32.zip'

		# URL de descarga para el número de versión específico de Edgedriver
		download_url = base_url.format(edge_version)

		# Descargar el archivo ZIP de Edgedriver
		response = requests.get(download_url)
				
		with open('edgedriver_win32.zip', 'wb') as f:
			f.write(response.content)

		# Descomprimir el archivo ZIP y mover el archivo Edgedriver a la ruta adecuada
		with zipfile.ZipFile('edgedriver_win32.zip', 'r') as zip_ref:
			zip_ref.extractall()
		os.replace('msedgedriver.exe', edgedriver)
	
		#sys.exit()
		
		option_edge = webdriver.EdgeOptions()
		option_edge.add_argument('--headless')
		option_edge.add_argument('--no-sandbox')
		option_edge.add_argument('--disable-dev-sh-usage')
		option_edge.add_argument('--disable-gpu')
		option_edge.add_argument("--disable-extensions")
		option_edge.add_argument("--log-level=3")
		option_edge.add_experimental_option('excludeSwitches', ['enable-logging']);
		
		service = Service(executable_path=edgedriver)
		service.creationflags = CREATE_NO_WINDOW
		
		return  webdriver.Edge(service=service, options=option_edge)
	except Exception as e:
		result = '--- error al instanciar webdriver para Edge---'
		logger.info(f'Exception: {result}')
		return


def message_error(msg):
	print('\033[31m' +msg +'\033[0m');

def message_success(msg):
	print('\033[32m' +msg +'\033[0m');
	

def message_warning(msg):
	print('\033[33m' +msg +'\033[0m');

if __name__ == "__main__":
	main()
