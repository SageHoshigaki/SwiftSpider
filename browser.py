from bs4 import BeautifulSoup as soup
import time
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import re
import csv
import json
import os
import random
import requests
import cloudscraper
import time
import sys
from parsel import Selector
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
import xlrd

class macro():
	def __init__(self):
		self.home= 'https://www.peoplesearchnow.com'
		filename='data.xlsx'
		wb = xlrd.open_workbook(filename)
		self.sheet = wb.sheet_by_index(0)


		# prefs = {"profile.managed_default_content_settings.images": 2}
		# chromeOptions.add_experimental_option("prefs", prefs)
		option = webdriver.ChromeOptions()
		chrome_prefs = {}
		option.experimental_options["prefs"] = chrome_prefs
		chrome_prefs["profile.default_content_settings"] = {"images": 2}
		chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
		option.add_argument("Block-image_v1.1.crx")
		# option.add_argument('--headless')
		option.add_argument('--no-sandbox')
		option.add_argument('--disable-dev-shm-usage')
		option.add_argument('--disable-logging')
		option.add_experimental_option("excludeSwitches", ["enable-logging"])
		# option.add_argument('--log-level 3')

		# firefox_profile = webdriver.FirefoxProfile()
		# firefox_profile.set_preference('permissions.default.image', 2)
		# firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
		self.driver= webdriver.Chrome(executable_path='chromedriver.exe',options=option)
		# self.driver = webdriver.Firefox(firefox_profile=firefox_profile)
	def wait_for_ajax(self,driver,wait_time):
	    wait = WebDriverWait(driver, wait_time)
	    try:
	        wait.until(lambda driver: driver.execute_script('return jQuery.active') == 0)
	        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
	        print('loaded!!')
	    except Exception as e:
	    	print('connection is slow')


	def scrape_section(self):
		last_line=[]
		for row in range(self.sheet.nrows):

			if row == 0:
				if os.path.exists('last.txt'):
					with open('last.txt','r') as file:
 						last_line.append(file.read().strip())
				else:
					last_line.append('0')
				print('last line -', str(last_line[0]))
				continue
			if row <= int(last_line[0]):
                # print(row)
				continue
			line_row =self.sheet.row_values(row)
			splits= self.sheet.row_values(row)
			first_name1= splits[8].strip()
			surname1= splits[9].strip()
			first_name2= splits[10].strip()
			surname2= splits[11].strip()
			Address = splits[0].strip().replace(' ','-')
			city= splits[2].strip()
			state= splits[3].strip()
			# number = splits[0].split(' ')[0]

			tasks =[]
			link='https://www.peoplesearchnow.com/address/%s_%s-%s'%(Address,city,state)
			print(row)
			print(link)

			# if len(Full_name1.strip())>5:
			tasks.append([link,'0'])
			# if len(Full_name2.strip())>5:
			# 	tasks.append(['https://www.peoplesearchnow.com/name/%s_%s'%(Full_name2,Address1),'1'])

			# print(last_line[0])
			if row ==(int(last_line[0])):
				s= requests.Session()

			phone1=''
			phone2=''

			try:
				self.driver.get(link)
				# self.wait_for_ajax(self.driver,10)
				print('getting %s'%link)
				if self.driver.title == 'Access to this page has been denied.':
					self.captcha_answer()
				answers= self.finduser(first_name1,surname1,first_name2,surname2)
				if answers==0:
					while True:
						check= Selector(text= self.driver.page_source).css('a.paginator-next::attr(href)').get()
						if check:
							print('going to the next page...')
							link='https://www.peoplesearchnow.com' +check
							self.driver.get(link)
							# self.wait_for_ajax(self.driver,10)
							if self.driver.title == 'Access to this page has been denied.':
									self.captcha_answer()
							answers= self.finduser(first_name1,surname1,first_name2,surname2)
							if answers != 0:
								break
						else:
							break

				print(answers)
				answer_links=[]
				if answers ==0:
					print('No user matches up!')
					# print('No phone number found!')
					self.write('None',['None','None'],line_row)
					print('success !!!')
					with open('last.txt','w') as file:
						file.write(str(row+1))

					continue
				else:
					for person in answers:
						name= person[0]
						answer_link= 'https://www.peoplesearchnow.com'+person[1]
						answer_links.append(answer_link)
			except Exception as e:
				print(e)


			try:
				all_phones=[]
				check=0
				for link in answer_links:
					self.driver.get(link)
					# print('getting %s'%answer_link)
					if self.driver.title == 'Access to this page has been denied.':
						self.captcha_answer()

					phone_numbers= self.find_phone()
					if phone_numbers !=0:
						check+=1
						# print('No phone numbers')
						# continue
					else:
						print('No phones found !!!')
						continue
					all_phones += phone_numbers
					# print(phone_numbers)

				if check ==0:
					print('No phone number found!')
					self.write('None',['None','None'],line_row)
					print('success !!!')
					with open('last.txt','w') as file:
						file.write(str(row+1))
					continue

				else:
					# print(all_phones)
					try:
						main_number= all_phones[0]
						other=all_phones[1:]
					except:
						print('No phone number found!')
						self.write('None',['None','None'],line_row)
						print('success !!!')
						with open('last.txt','w') as file:
							file.write(str(row+1))
						continue


				print(main_number,other)
			except Exception as e:
				print(e)
			try:
				self.write(main_number,other,line_row)
				print('success !!!')

				with open('last.txt','w') as file:
					file.write(str(row+1))
			except:
				print('No phone number found!')
				self.write('None',['None','None'],line_row)
				print('success !!!')
				with open('last.txt','w') as file:
					file.write(str(row+1))
				continue






	def finduser(self,first_name1,surname1,first_name2,surname2):
		print(first_name1,surname1,first_name2,surname2)
		# self.wait_for_ajax(self.driver,15)
		response = Selector(text =self.driver.page_source)
		names= response.css('div.result-search-block p.ellipsis.pull-left::text').extract()
		# print(names)
		hrefs= response.css('div.result-search-block a.btn.btn-success.pull-right::attr(href)').extract()
		answers=[]
		for name, href in zip(names,hrefs):
			if first_name1 !='' and surname1 !='' and first_name1.lower() in name.lower() and surname1.lower() in name.lower():
				answer= (name,href)
				print('User found!')
				print('here1')
				# print(names)
				# print(hrefs)
				# print(anwser)
				answers.append(answer)
				break
				# return answer
		for name, href in zip(names,hrefs):
			if first_name2 !='' and surname2 !='' and first_name2.lower() in name.lower() and surname2.lower() in name.lower():
				answer= (name,href)
				answers.append(answer)
				print('User found!')
				print('here2')
				break
				# return answer
		if len(answers)==0:
			print('No user found on this page !!!')
			return 0
		else:
			return answers

	def find_phone(self):
		response = Selector(text =self.driver.page_source)
		# main_phone= response.xpath('//*[@itemprop="telephone"]/text()').get()
		# landlines= response.css('div.result-full-info-content').extract()[2]
		phone_numbers= re.findall("\(\d{3}\) \d{3}-\d{4}\W\w{6,9}",self.driver.page_source)
		# print(phone_numbers)
		# sys.exit('Done')

		if len(phone_numbers) >1:
			# main_number= phone_numbers[0]
			# others= phone_numbers[1:]
			# return((main_number,others))
			return phone_numbers
		elif len(phone_numbers) ==1:
			# main_number= phone_numbers[0]
			# others= []
			# return((main_number,others))
			return phone_numbers
		elif len(phone_numbers)==0:
			return 0






	def captcha_answer(self):
		print('########  Solving captcha  ########')
		response = Selector(text= self.driver.page_source)
		site_key= response.css('div.g-recaptcha::attr(data-sitekey)').get()
		callback = response.css('div.g-recaptcha::attr(data-callback)').get()
		_2captcha_key='fb5d6af44901ae3ab67ac29441cc3aa2'
		# print(site_key)

		data_2cap = {'key': _2captcha_key,
                         'method': 'userrecaptcha',
                         'googlekey': site_key,
                         'pageurl': self.driver.current_url,
                         'invisible': '0',
                         'json': '0'}
		r = requests.get(
                f'https://2captcha.com/in.php?key={data_2cap["key"]}&method=userrecaptcha&googlekey={data_2cap["googlekey"]}&pageurl={data_2cap["pageurl"]}&invisible=1')
		captcha_id = r.text.split('|')[1]
		# print(r.text)
		# print(captcha_id)
		r = requests.get(f'https://2captcha.com/res.php?key={data_2cap["key"]}&action=get&id={captcha_id}')
		# print(r.text)
		status = r.text.split('|')[0]
		i = 0
		while status != 'OK':
			print(f'{i}-Status is not OK, trying in 2 to 4  seconds-{status}')
			r = requests.get(f'https://2captcha.com/res.php?key={data_2cap["key"]}&action=get&id={captcha_id}')
			status = r.text.split('|')[0]
			i += 1
			time.sleep(random.uniform(2, 4))
		print('Succcess !!!')

		token_g = r.text.split('|')[1]
		# print(token_g)
		js1 = f'document.getElementById("g-recaptcha-response").innerHTML="{token_g}";'
		# print(js1)
		self.driver.execute_script(js1)

		js2 = f'{callback}("{token_g}");'
		# print(js2)
		self.driver.execute_script(js2)
		print('Done with captcha')
		time.sleep(random.uniform(3, 4))

	def write(self,main,others,line_row):
		other_phones=[]
		for index in range(12):
			try:
				other_phones.append(others[index])
			except:
				other_phones.append('None')


		next_line =[field for field in line_row] + [main, other_phones[0], other_phones[1],other_phones[2],other_phones[3],other_phones[4],other_phones[5],other_phones[6],other_phones[7],other_phones[8],other_phones[9],other_phones[10],other_phones[11]]


		if not os.path.exists('output.csv'):
			with open('output.csv', 'w',newline='') as file:
				writer= csv.writer(file)
				line=['Address','Unit #','City','State','Zip','County','APN','Owner Occupied','Owner 1 First Name','Owner 1 Last Name','Owner 2 First Name','Owner 2 LastName','Mailing Care of Name','Mailing Address','Mailing Unit #','Mailing City','Mailing State','Mailing Zip','Mailing County','Do Not Mail','Property Type','Bedrooms','Total Bathrooms','Building Sqft','Lot Size Sqft','Effective Year Built','Total Assessed Value','Last Sale Recording Date','Last Sale Amount','Toal Open Loans','Est. Remaining balance of Open Loans','Est. Value','Est. Loan-to-Value','Est. Equity','MLS Status','MLS Date','MLS Amount','Lien Amount','Marketing Lists','Date Added to List','Method of Add','Current Phone Number','Other Phone 1','Other Phone 2','Other Phone 3','Other Phone 4','Other Phone 5','Other Phone 6','Other Phone 7','Other Phone 8','Other Phone 9','Other Phone 10','Other Phone 11','Other Phone 12']

				writer.writerow(line)
				writer.writerow(next_line)
		else:
			with open('output.csv', 'a',newline='') as file:
				writer= csv.writer(file)
				writer.writerow(next_line)



	def clean(self,variable):
		pass
	def dump_result(self):
		pass




if __name__ == "__main__":
	macro= macro()
	macro.scrape_section()
