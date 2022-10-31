from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

import sys
import time
import requests
from requests.structures import CaseInsensitiveDict

import os
from dotenv import load_dotenv
import re
from datetime import date

os.system("rm available_tickets.txt")
os.system("touch available_tickets.txt")

load_dotenv()

SHOW_PREFIX=os.getenv('SHOW_PREFIX')

if SHOW_PREFIX is None:
    try:
        SHOW_PREFIX = sys.argv[1]
    except:
        print("SHOW_PREFIX value not specified in environment or as parameter. Please create a .env file in ./src or pass an argument.")
        exit()


BLINK_IP=os.getenv('BLINK_IP')
IFTTT_KEY=os.getenv('IFTTT_KEY')
IFTTT_EVENT=os.getenv('IFTTT_EVENT')
IFTTT_MESSAGE=os.getenv('IFTTT_MESSAGE')
DATE_RANGE=os.getenv('DATE_RANGE')


starting_date = date.today()
ending_date = date(2049, 12, 31)

def send_notification(course):
    # print("Call no ", course.call_no)

    ifile=open("available_courses.txt" ,"r")
    lines = ifile.readlines()
    ifile.close()

    request_sent = False

    for line in lines:
        # print("line",line)
        # print("course call no",course.call_no)
        if line[0:line.index("\n")] == course.call_no:
            request_sent = True

    if request_sent == False:
        print(f"Request for {course.course_no} {course.section_no} not sent, sending request.")
        ifttt_url = f"https://maker.ifttt.com/trigger/{IFTTT_EVENT}/json/with/key/{IFTTT_KEY}"

        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"
        headers["Content-Type"] = "application/json"

        # print(f"Message: {IFTTT_MESSAGE} {course.course_title} {course.course_no} {course.section_no} {course.call_no} {course.status} {course.professor}")

        data = f"""
        {{
            "Message": "{IFTTT_MESSAGE} {course.course_title} {course.course_no} {course.section_no} {course.call_no} {course.status} {course.professor}"
        }}
        """

        resp = requests.post(ifttt_url, headers=headers, data=data)
        print("Request response:", resp.status_code)

        oFile = open("available_courses.txt", "a")
        oFile.write(course.call_no + "\n")
        oFile.close()

        try:
            requests.get(f"{BLINK_IP}/fade?color=green")
        except:
            pass

    # else:
        # print(f"Request for {course.course_no} {course.section_no} already sent")


def process_date_range():

    global starting_date
    global ending_date

    # print(starting_date)
    # print(ending_date)

    try:
        my_date = DATE_RANGE[0:8]
        # print(my_date)

        year = int(my_date[0:4])
        month = int(my_date[4:6])
        day = int(my_date[6:8])
        # print(year, month, day)

        # if starting_date != None:
        starting_date= date(year,month,day)

    except:
        pass

    try:
        my_date = DATE_RANGE[9:17]

        year = int(my_date[0:4])
        month = int(my_date[4:6])
        day = int(my_date[6:8])

        ending_date= date(year,month,day)

    except:
        pass

    # print(starting_date)
    # print(ending_date)


def main():

    process_date_range()

    # time.sleep(500)

    try:
        user_agent = "Mozilla/5.0 (Windows NT 10.0; rv:103.0) Gecko/20100101 Firefox/103.0"

        options = webdriver.FirefoxOptions()
        # options.headless = True
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument("--window-size=1920,1080")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument("--disable-extensions")
        options.add_argument("--proxy-server='direct://'")
        options.add_argument("--proxy-bypass-list=*")
        options.add_argument("--start-maximized")
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')

        driver = webdriver.Firefox(options=options)


        wait = WebDriverWait(driver, 10)

        driver.get(SHOW_PREFIX)

        wait.until(presence_of_element_located((By.XPATH, "//a[contains(@class, 'CalendarEvents__EventLink')]")))

        event_links_present = True


        links = []

        itercount = 0

        # WHILE LOOP TO KEEP CLICKING "SHOW MORE DATES"
        while(event_links_present and presence_of_element_located((By.CLASS_NAME, "Typography__Text1-sc-7500c16d-6"))):
            # show_more_dates_button = driver.find_element(by=By.CLASS_NAME, value="Typography__Text1-sc-7500c16d-6 jkUBWq")
            show_more_dates_button = driver.find_element(by=By.CLASS_NAME, value="Typography__Text1-sc-7500c16d-6")
            show_more_dates_button.click()

            month_wrappers = driver.find_elements(by=By.CLASS_NAME, value="Month__Wrapper-sc-b4a14563-5")

            last_month = month_wrappers[len(month_wrappers) - 1]

            print(itercount)

            # time.sleep(500)

            # for wrapper in month_wrappers:

                # days = wrapper.find_elements(by=By.CLASS_NAME, value="CalendarEvents__Events-sc-19173feb-5")

                # for day in days:
                    # print("day")
                # print("Wrapper found")
                # print(wrapper.get_attribute("innerHTML"))

            month_name = last_month.find_element(by=By.CLASS_NAME, value="Typography__Heading3-sc-7500c16d-2")
            month_name = month_name.get_attribute("innerHTML")
            print(month_name)

            # events = last_month.find_elements(by=By.XPATH,value="//a[contains(@class, 'CalendarEvents__EventLink')]")
            events = last_month.find_elements(by=By.CLASS_NAME, value="CalendarEvents__EventLink-sc-19173feb-7")
            if(len(events) == 0):
                # print("length = 0")
                event_links_present = False
                break

            else:
                for event in events:
                    link = event.get_attribute("href")
                    try:
                        link_date = link[link.index("20"):link.index("-pm")]
                        year = int(link_date[0:4])
                        month = int(link_date[5:7])
                        day = int(link_date[8:10])
                        mytime = int(link_date[11])
                        matinee = False        
                        if(mytime < 4):
                            matinee = True
                        else:
                            matinee = False
                        print(year, ",", month, ",", day, ",", mytime )

                        mydate = date(year, month, day)
                        if mydate > ending_date:
                            print("Reached limit")
                            event_links_present = False
                            break




                    except:
                        pass

            time.sleep(5)

            itercount = itercount+ 1




        time.sleep(500)
        # BELOW HERE IS GARBAGE

        links = []
        events = driver.find_elements(by=By.XPATH,value="//a[contains(@class, 'CalendarEvents__EventLink')]")
        for event in events:
            link = event.get_attribute("href")
            try:
                link_date = link[link.index("20"):link.index("-pm")]
                year = int(link_date[0:4])
                month = int(link_date[5:7])
                day = int(link_date[8:10])
                mytime = int(link_date[11])
                matinee = False        
                if(mytime < 4):
                    matinee = True
                else:
                    matinee = False
                print(year, ",", month, ",", day, ",", mytime )
            except:
                pass



        time.sleep(500)
        exit()
        for link in links:
            driver.get(link)
            time.sleep(5)


        time.sleep(500)
        exit()
        time.sleep(1)
        network_id = driver.find_element(by=By.XPATH,value='/html/body/div[3]/main/table/tbody/tr/td[1]/form/table/tbody/tr[2]/td[2]/input')
        network_password = driver.find_element(by=By.XPATH,value='//*[@id="u_pw"]')
        network_id.send_keys(CU_ID)
        network_password.send_keys(CU_PASS)
        login_button = driver.find_element(by=By.XPATH,value='/html/body/div[3]/main/table/tbody/tr/td[1]/form/table/tbody/tr[4]/td/input')
        login_button.click()

        wait.until(presence_of_element_located((By.XPATH, '//*[@id="AppName"]')))
        time.sleep(1)

        registration_button = driver.find_element(by=By.XPATH,value="//*[ text() = 'Registration' ]")
        registration_button.click()

        wait.until(presence_of_element_located((By.XPATH, '/html/body/div[3]/main/form[2]/fieldset/input[2]')))
        time.sleep(1)
        continue_button = driver.find_element(by=By.XPATH,value='/html/body/div[3]/main/form[2]/fieldset/input[2]')

        continue_button.click()

        wait.until(presence_of_element_located((By.XPATH, '/html/body/div[3]/main/form[2]/table/tbody/tr[2]/td[1]/input')))
        time.sleep(1)
        call_no = driver.find_element(by=By.XPATH,value='/html/body/div[3]/main/form[2]/table/tbody/tr[2]/td[1]/input')
        query_button = driver.find_element(by=By.XPATH,value='/html/body/div[3]/main/form[2]/table/tbody/tr[2]/td[2]/input')
        call_no.send_keys(COURSE_SEARCH)
        query_button.click()


        while True:
            # wait.until(presence_of_element_located((By.XPATH, "//*[ contains (text(), 'Search results for' ) ]")))
            wait.until(presence_of_element_located((By.XPATH, "/html/body/div[3]/main/form[3]/table/tbody/tr[1]/td")))
            time.sleep(1)

            white_classes = driver.find_elements(by=By.CLASS_NAME,value='cls0W')
            gray_classes = driver.find_elements(by=By.CLASS_NAME,value='cls0')
            open_classes = white_classes + gray_classes
            # CLASS OF INTEREST: cls0W
            for open_class in open_classes:
                my_course = Course()

                # print(white_class)
                # print(white_class["td[3]"].get_attribute("innerHTML"))
                table_datas = open_class.find_elements(by=By.TAG_NAME,value="td")


                for table_data in table_datas:
                    inner_html = table_data.get_attribute("innerHTML")
                    # print(inner_html)
                    # print(table_data.get_attribute("innerHTML"))
                    if "CALLNUM" in inner_html:
                        call_no = re.findall(r"\D(\d{5})\D", inner_html)[0]
                        my_course.setCallNo(call_no)
                    if COURSE_SEARCH[0:COURSE_SEARCH.index(" ")] in inner_html:
                        course_no = inner_html[inner_html.index(COURSE_SEARCH[0:COURSE_SEARCH.index(" ")]):(inner_html.index("sec") - 2)]
                        my_course.setCourseNo(course_no)
                        section_no = inner_html[(inner_html.index("sec") + 4):(inner_html.index("sec") + 7)]
                        my_course.setSectionNo(section_no)
                        course_title = inner_html[(inner_html.index("clnm") + 6):inner_html.index("</font>")].strip()
                        my_course.setCourseTitle(course_title)
                        # print(inner_html)
                    # if inner_html.count(" ") == 3:
                        # my_course.setProfessor(inner_html.strip())
                    if "Open" in inner_html:
                        my_course.setStatus("Open")

                professor = table_datas[2].get_attribute("innerHTML").strip()
                professor = re.sub(' +', ' ', professor)
                my_course.setProfessor(professor)


                if my_course.getStatus() == "Open":
                    # my_course.setStatus("Not Open")

                    if use_whitelist:
                        if my_course.section_no in sections_of_interest:
                            send_notification(my_course)
                    else:
                        if my_course.section_no not in sections_of_interest:
                            send_notification(my_course)

                # print(my_course.course_no)
                # print(my_course.call_no)
                # print(my_course.status)
                # print(my_course.section_no)
                # print(my_course.course_title)
                # print()

            # print("SLEEPING THIS ROUND")
            time.sleep(10)
            search_class_button = driver.find_element(by=By.XPATH,value='/html/body/div[3]/main/form[2]/center/input[2]')
            driver.refresh()

        driver.quit()
    except KeyboardInterrupt:
        driver.quit()
    except Exception as e:
        print(f"EXCEPTION: {e}")
        #driver.quit()



if __name__ == "__main__":
    main()

