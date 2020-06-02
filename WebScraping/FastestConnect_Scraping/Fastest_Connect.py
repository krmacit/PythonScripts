from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import csv
import os

def openFastestConnect():
    url = "http://seaburycargo.com/ibmcognos/cgi-bin/cognosisapi.dll"
    
    capabilities = { 'chromeOptions':  { 'useAutomationExtension': False}}
    
    # Open browser
    driver = webdriver.Chrome(desired_capabilities = capabilities)
    
    try:
        driver.implicitly_wait(30)
        driver.get(url)
        
        # Login
        driver.find_element_by_id("CAMUsername").send_keys("****")
        driver.find_element_by_id("CAMPassword").send_keys("****")
        driver.find_element_by_id("cmdOK").send_keys(Keys.ENTER)
        
        # Open Fastest Connect and wait for load
        driver.find_element_by_link_text("Seabury - Capacity Airline Reports").send_keys(Keys.ENTER)
        driver.find_element_by_link_text("Fastest connect").send_keys(Keys.ENTER)
        WebDriverWait(driver, 600).until(EC.presence_of_element_located((By.CLASS_NAME, "tableRow")))
        
        # Select and run table
        driver.find_element_by_xpath(
            "/html/body/form[1]/table/tbody/tr[3]/td/div/div/table/tbody/tr/td/table[3]/tbody/tr[1]/td/fieldset/table/tbody/tr[2]/td[1]/div/table/tbody/tr/td/div/select/option[1]").click()
        driver.find_element_by_xpath(
            "/html/body/form[1]/table/tbody/tr[3]/td/div/div/table/tbody/tr/td/table[3]/tbody/tr[1]/td/fieldset/table/tbody/tr[2]/td[2]/div/table/tbody/tr/td/div/select/option[1]").click()
        driver.find_element_by_xpath("//*[starts-with(@id, 'finish')]").send_keys(Keys.ENTER)
        
        # Yüklenmesini bekle ve Tümünü seç ve yüklenmesini bekle
        WebDriverWait(driver, 600).until(EC.presence_of_element_located((By.CLASS_NAME, "tableCell")))
        driver.find_element_by_link_text("Select all").send_keys(Keys.ENTER)
        driver.find_element_by_xpath("//*[starts-with(@id, 'finish')]").send_keys(Keys.ENTER)
        driver.implicitly_wait(0)
        WebDriverWait(driver,600).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/table/tbody/tr/td/div/table/tbody/tr[1]/td[1]/img")))
        WebDriverWait(driver,600).until(EC.invisibility_of_element_located((By.XPATH, "/html/body/div[3]/table/tbody/tr/td/div/table/tbody/tr[1]/td[1]/img")))
        driver.implicitly_wait(30)
    except Exception: 
        pass
    return driver



#time
start_time = time.time()

HeaderList = {"Carrier(s)", "Equipment", "Max load (tonnes)", "Departure day", "Departure time", "Connection", "Transit time (dd:hh:mm)", "Days to arrival", "Arrival day", "Arrival time", "Total time (dd:hh:mm)", "Time to next flight (dd:hh:mm)", "Origin", "Destination"}
outputData = pd.DataFrame(columns = HeaderList)

ErroredOrgDes = pd.DataFrame(columns=['Org', 'Des'])

driver = openFastestConnect()

count = 0;
count100 = 0;

print("Opening Website  --- {:.1f} seconds ---".format(time.time() - start_time))

start_fetching_time = time.time()
with open('Org_Des.csv', 'r') as odcsvfile:
    odpairs = csv.reader(odcsvfile)
    for odpair in odpairs:
        try:
            print("{}->{}".format(odpair[0],odpair[1]), end =" ")
            inputdriver = driver.find_elements_by_xpath("(//*[starts-with(@id, 'PRMT_TB_')])")[0]
            inputdriver.send_keys(3*Keys.BACKSPACE)
            inputdriver.send_keys(odpair[0])
            inputdriver = driver.find_elements_by_xpath("(//*[starts-with(@id, 'PRMT_TB_')])")[1]
            inputdriver.send_keys(3*Keys.BACKSPACE)
            inputdriver.send_keys(odpair[1])
            driver.find_element_by_xpath("//*[starts-with(@id, 'finish')]").send_keys(Keys.ENTER)
            driver.implicitly_wait(0)
            WebDriverWait(driver,600).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/table/tbody/tr/td/div/table/tbody/tr[1]/td[1]/img")))
            WebDriverWait(driver,600).until(EC.invisibility_of_element_located((By.XPATH, "/html/body/div[3]/table/tbody/tr/td/div/table/tbody/tr[1]/td[1]/img")))
            time.sleep(1)            
            table=pd.read_html(driver.page_source)
            data = table[0]
            data = data.iloc[95:-2]
            data['13'] = odpair[0]
            data['14'] = odpair[1]
            data.columns = HeaderList
            outputData = outputData.append(data)
            if(count < 99):
                count+=1
            else:
                count100 += 1
                print("\n{} Data Fetched in --- {:.1f} minutes ---".format((count100*100), (time.time() - start_fetching_time)/60))
                count = 0
        except:
            print("\n\nException occured, in {} and {}".format(odpair[0],odpair[1]))
            print("After 10 sec, loop going to continue\n")
            time.sleep(10)
            ErroredOrgDes = ErroredOrgDes.append({'Org': odpair[0], 'Des': odpair[1]}, ignore_index=True)
            try:
                driver.quit()
            except Exception: 
                pass
            driver = openFastestConnect()

dirpath = os.getcwd()
ErroredOrgDes.to_csv(os.path.join(dirpath,r'Errors\errors.csv'))
ErroredOrgDes.to_excel(os.path.join(dirpath,r'Errors\errors.xlsx'))
    
outputData.columns = HeaderList
print("Finished Fetching in  --- {:.1f} minutes ---".format((time.time() - start_time)/60))

start_exp_time = time.time()
outputData.to_csv(os.path.join(dirpath,r'Results\fastestConnect.csv'))           
print("Exporting to CSV in  --- {:.1f} minutes ---".format((time.time() - start_exp_time)/60))

start_exp_time = time.time()
outputData.to_excel(os.path.join(dirpath,r'Results\fastestConnect.xlsx'))    
print("Exporting to xlsx in  --- {:.1f} minutes ---".format((time.time() - start_exp_time)/60))

print("Total time passed:  --- {:.1f} hours ---".format((time.time() - start_time)/360))
            
driver.quit()
