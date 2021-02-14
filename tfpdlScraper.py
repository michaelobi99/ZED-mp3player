from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from typing import List
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import datetime
import pyautogui
tfpdl_videoDownloadCancelledFlag = Queue(maxsize=1)
tfpdl_videoDownloadErrors = Queue(maxsize=2)
tfpdl_videoDownloadNotification = Queue(maxsize=2)
from voicemessages import fileFoundMessage, searchMessage

class TFPDLVideoDownload():
    def __init__(self):
        self.chromeOptions = self.chromeOptions1 = Options()
        self.chromeOptions.add_argument('--disable-notifications')
        self.chromeOptions1.add_argument('--disable-notifications')
        #self.chromeOptions.add_argument('--headless')
        self.driver = None
        self.downloadPath = r'C:\Users\HP\Downloads'
        self.fileDownloaded = False #used to notify checkDownloadCancelled function
        self.selector = """div[class = 'wrapper full-site'] div[class = 'container'] div[id = 'main-content'] 
        div[class = 'content-wrap'] div[class = 'content'] """
        self.resolution = "480p"
        self.fileDownloaded = False

    def parse(self, num: int):
        if (num < 10):
            return '0' + str(num)
        return str(num)

    def findMovieLink(self, driver, string):
        while True:
            try:
                linksOnCurrentPage = WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, f'''{self.selector} div[class = 'post-listing '] article h2 a''')))
                print(f'length = {len(linksOnCurrentPage)}')
                for link in linksOnCurrentPage:
                    strLink = str(link.get_attribute('href'))
                    print(strLink)
                    if string in strLink and self.resolution in strLink and 'complete' not in strLink:
                        print(f'found link -> {strLink}')
                        return link
                nextPage = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, f'''{self.selector} div[class = 'pagination'] span[id = 'tie-next-page'] a''')))
                sleep(2)
                nextPage.click()
            except IndexError as error:
                raise error
            except ElementClickInterceptedException as error:
                raise error
            except NoSuchElementException as error:
                raise error
            except TimeoutException as error:
                raise error
            except WebDriverException as error:
                raise error

    def getFileLink(self, driver):
        try:
            for tab in driver.window_handles:
                driver.switch_to.window(tab)
                if 'xproxxx' in driver.title:
                    break
            assert 'xproxxx' in driver.title, "ERROR: can't find correct tab"
            #proceed for links
            print(driver.title)
            action1 = ActionChains(driver)
            link1 = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, '''form[id = 'landing'] div[id = 'landing'] div[class = 'wait'] center img''')))
            action1.move_to_element(link1).click().perform()
            #link1.click()
            #generate links
            sleep(1.5)
            print(driver.title)
            action2 = ActionChains(driver)
            link2 = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[id = 'landing'] div[class = 'to'] a")))
            action2.move_to_element(link2).click().perform()
            #link2.click()
            #view links
            sleep(1.5)
            print(driver.title)
            action3 = ActionChains(driver)
            link3 = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".spoint")))
            #link3.click()
            action3.move_to_element(link3).click().perform()

            sleep(1.5)
            if 'safe.txt' not in driver.title:
                self.moveToCorrectTab(driver, 'safe.txt')

            #send keys and submit form
            form: List = WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "form[method = 'post'] p input")))
            innerParagraphs = driver.find_elements_by_css_selector("form[method = 'post'] p")
            if len(innerParagraphs) == 3:
                raise Exception("ERROR: A captcha challenge is blocking the progress of the crawler")
            elif len(innerParagraphs) == 2:
                password = 'tfpdl'
                for char in password:
                    form[0].send_keys(char)
                sleep(1)
                form[1].click()
            fileLink = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href ^= 'https://firefiles']")))
            return fileLink

        except AssertionError as error:
            raise error
        except ElementClickInterceptedException as error:
            raise error
        except NoSuchElementException as error:
            raise error
        except TimeoutException as error:
            raise error
        except WebDriverException as error:
            raise error
        except BaseException as error:
            raise error

    def moveToCorrectTab(self, driver, expectedTitle):
        for index in range(len(driver.window_handles)):
            driver.switch_to.window(driver.window_handles[index])
            if expectedTitle in driver.title:
                break

    def clickFirstDownloadButton(self,xPosition=0, yPosition=0):
        tabsNum = len(self.driver.window_handles)
        pyautogui.scroll(-100)
        sleep(2)
        pyautogui.moveTo(xPosition, yPosition)
        sleep(2)
        pyautogui.doubleClick()
        if len(self.driver.window_handles) > tabsNum:
            print('got here')
            sleep(2)
            self.driver.switch_to.window(self.driver.window_handles[0])
            print('switched back to first window')
            sleep(2)
            pyautogui.scroll(-100)
            sleep(2)
            pyautogui.moveTo(xPosition, yPosition)
            sleep(2)
            pyautogui.doubleClick()
        sleep(5)

    def clickSecondDownloadButton(self, button: str):
        lenOfTabs = len(self.driver.window_handles)
        pyautogui.scroll(-200)
        sleep(2)
        location = pyautogui.locateOnScreen(button)
        if location == None:
            print('Image not found on screen')
        else:
            print('found button')
            pyautogui.doubleClick(location)
            sleep(5)
        if (self.driver.window_handles > lenOfTabs):
            self.driver.switch_to.window(self.driver.window_handles[0])

    def clickThirdDownloadButton(self, button: str):
        pyautogui.scroll(-200)
        sleep(2)
        location = pyautogui.locateOnScreen(button)
        if location == None:
            print('Image not found on screen')
        else:
            print('found button')
            pyautogui.doubleClick(location)
            sleep(5)

    def checkDownloadCancelled(self):
        while tfpdl_videoDownloadCancelledFlag.qsize() == 0 and tfpdl_videoDownloadErrors.qsize() == 0:
            pass
        if tfpdl_videoDownloadCancelledFlag.qsize() == 1:
            tfpdl_videoDownloadErrors.put("Download cancelled", block=False)

    def checkFilePresence(self, numberOfFilesInitially, timeNow, extension):
        found = False
        while not found and tfpdl_videoDownloadErrors.qsize() == 0:
            numberOfFilesNow = len(os.listdir(self.downloadPath))
            if numberOfFilesNow > numberOfFilesInitially:
                for folders, subfolders, files in os.walk(self.downloadPath):
                    for file in files:
                        try:
                            creationTime = datetime.datetime.fromtimestamp(
                                os.path.getctime(os.path.join(folders, file)))
                            if creationTime > timeNow:
                                if file.endswith(extension):
                                    self.fileDownloaded = True
                                    return
                        except FileNotFoundError:
                            tfpdl_videoDownloadErrors.put("FILE NOT FOUND", block=False)
                        except BaseException as error:
                            tfpdl_videoDownloadErrors.put(error, block = False)

    def connectionCheck(self):
        while self.fileDownloaded == False and tfpdl_videoDownloadErrors.qsize() == 0:
            try:
                self.driver.switch_to.window(self.driver.window_handles[1])
                self.driver.get('https://google.com')
                sleep(10)
            except WebDriverException as error:
                tfpdl_videoDownloadErrors.put(error)
                break

    def download(self, movieName: str, season: str = '', episode: str = ''):
        if movieName == '':
            tfpdl_videoDownloadErrors.put('ERROR: Movie name field cannot be empty')
            raise BaseException
        else:
            try:
                searchMessage()
                executor = ThreadPoolExecutor(max_workers=3)
                downloadCancelCheck = executor.submit(self.checkDownloadCancelled)
                movieName = '+'.join(movieName.split())
                season, episode = self.parse(int(season)), self.parse(int(episode))
                string = 's' + season + 'e' + episode
                print(string)
                self.driver = webdriver.Chrome(options=self.chromeOptions)
                url = r'https://tfp.is/?s=' + movieName
                self.driver.minimize_window()
                self.driver.get(url)
                self.driver.get_cookies()
                movieLink = self.findMovieLink(self.driver, string)
                sleep(1)
                movieLink.click()
                downloadButton = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, f'''{self.selector} article \
                                        div[class = 'post-inner'] div[class = 'entry'] a[href ^= 'https://www.tfp.is']''')))
                print(downloadButton.get_attribute("href"))
                self.driver.get(downloadButton.get_attribute("href"))
                downloadFileLink = self.getFileLink(self.driver).get_attribute('href')
                print(downloadFileLink)
                sleep(2)
                self.driver.quit()
                numberOfFilesInitially = len(os.listdir(self.downloadPath))
                timeNow = datetime.datetime.now()
                fileChecker = executor.submit(self.checkFilePresence, (numberOfFilesInitially, timeNow, '.mkv'))
                self.driver = webdriver.Chrome(options=self.chromeOptions1)
                self.driver.get(downloadFileLink)
                self.driver.maximize_window()
                self.clickFirstDownloadButton(667, 539)
                self.clickSecondDownloadButton("button2.png")
                fileFoundMessage()
                self.clickThirdDownloadButton("button1.png")
                connectionChecker = executor.submit(self.connectionCheck)
                self.driver.minimize_window()
                for downloadResult in as_completed({downloadCancelCheck, fileChecker, connectionChecker}):
                    downloadResult.result()

            except IndexError as error:
                self.driver.quit()
                tfpdl_videoDownloadErrors.put(error, block=False)
                raise error
            except AssertionError as error:
                self.driver.quit()
                tfpdl_videoDownloadErrors.put(error, block=False)
                raise error
            except ElementClickInterceptedException as error:
                self.driver.quit()
                tfpdl_videoDownloadErrors.put(error, block=False)
                raise error
            except NoSuchElementException as error:
                self.driver.quit()
                tfpdl_videoDownloadErrors.put(error, block=False)
                raise error
            except TimeoutException as error:
                self.driver.quit()
                tfpdl_videoDownloadErrors.put(error, block=False)
                raise error
            except ElementNotInteractableException as error:
                self.driver.quit()
                tfpdl_videoDownloadErrors.put(error, block=False)
                raise error
            except WebDriverException as error:
                self.driver.quit()
                tfpdl_videoDownloadErrors.put(error, block=False)
                raise error
            except BaseException as error:
                self.driver.quit()
                tfpdl_videoDownloadErrors.put(error, block=False)
                raise error
            else:
                self.driver.quit()
