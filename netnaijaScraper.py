from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException, NoSuchAttributeException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from queue import Queue
import os
import datetime
from threading import Thread
chromeOptions = Options()
chromeOptions.add_argument('--disable-notifications')
fileLink = []
videoDownloadErrors = Queue(maxsize=1)
videoDownloadNotification = Queue(maxsize=2)

class VideoDownLoad():
    def __init__(self):
        self.driver = None
        self.driver1 = None
        self.driver2 = None
        self.downloadPath = r'C:\Users\HP\Downloads'

    def checkFilePresence(self, numberOfFilesInitially, timeNow, extension):
        downloadPath = r'C:\Users\HP\Downloads'
        found = False
        while not found:
            numberOfFilesNow = len(os.listdir(downloadPath))
            if numberOfFilesNow > numberOfFilesInitially:
                for folders, subfolders, files in os.walk(downloadPath):
                    for file in files:
                        try:
                            creationTime = datetime.datetime.fromtimestamp(os.path.getctime(os.path.join(folders, file)))
                            if creationTime > timeNow:
                                if file.endswith(extension):
                                    videoDownloadNotification.put(True)
                                    return
                        except FileNotFoundError:
                            pass
                        except BaseException:
                            pass

    def startSRTDownload(self, link):
        self.driver2 = webdriver.Chrome(options=chromeOptions)
        self.driver2.get(link)
        try:
            numberOfFilesInitially = len(os.listdir(r'C:\Users\HP\Downloads'))
            timeNow = datetime.datetime.now()
            downloadButton = self.driver2.find_element_by_css_selector(
            """div[id = 'app-content'] div[id = 'file-page'] div[id = 'action-buttons'] button""")
            downloadButton.click()
            fileChecker = Thread(target=self.checkFilePresence, args=[numberOfFilesInitially, timeNow, r'.srt'])
            fileChecker.start()
            fileChecker.join()
        except NoSuchElementException as error:
            videoDownloadErrors.put(error)
            raise
        finally:
            self.driver2.quit()

    def startMP4Download(self, link):
        self.driver1 = webdriver.Chrome(options=chromeOptions)
        self.driver1.get(link)
        try:
            numberOfFilesInitially = len(os.listdir(r'C:\Users\HP\Downloads'))
            timeNow = datetime.datetime.now()
            downloadButton = self.driver1.find_element_by_css_selector("""div[id = 'app-content'] div[id = 'file-page'] div[id = 'action-buttons'] button""")
            downloadButton.click()
            fileChecker = Thread(target=self.checkFilePresence, args=[numberOfFilesInitially, timeNow, r'.mp4'])
            fileChecker.start()
            fileChecker.join()
        except NoSuchElementException as error:
            videoDownloadErrors.put(error)
        finally:
            self.driver1.quit()

    def quitDownload(self):
        self.driver.quit()
        self.driver1.quit()
        self.driver2.quit()


    def search(self, string, link):
        return string in link

    def findFileLink(self, movie_name, _season=0, _episode=0):
        global fileLink
        if movie_name == '':
            videoDownloadErrors.put('ERROR: Movie name field cannot be empty')
            raise
        else:
            movieName = movie_name
            episode = "episode-" + str(_episode)
            season = "season-" + str(_season)
            if season == 'season-0' or episode == 'episode-0':
                season, episode = '', ''
            folder = "Video"
            print(season, episode)
            try:
                self.driver = webdriver.Chrome(options=chromeOptions)
                self.driver.get("http://netnaija.com/search")
                input1 = self.driver.find_element_by_css_selector("div[class = 'row'] div[class='input'] input")
                for elem in movieName:
                    input1.send_keys(elem)
                    sleep(.2)
                input2 = self.driver.find_element_by_css_selector("div[class = 'row'] div[class='input'] select")
                input2.send_keys(folder)
                input2.submit()
                sleep(3)
                links = self.driver.find_elements_by_css_selector('''div[id= 'search-page'] div[id = 'search-results'] main[class = 'search-results-list'] \
                                                             article[class = 'result'] div[class = 'result-info'] h3[class = 'result-title'] a''')
                self.found = False
                while not self.found:
                    for link in links:
                        l = link.get_attribute('href')
                        print(l)
                        if self.search(episode, str(l)) and self.search(season, str(l)):
                            print(f'found link -> {l}')
                            self.found = True
                            link.click()
                            break
                    if not self.found:
                        try:
                            nextPage = self.driver.find_element_by_css_selector('''div[class = 'pages'] div[class = 'page-listing'] span[class = 'a-page'] \
                                                                        a[title = 'Next Page']''')
                            print("Going to the next page")
                            nextPage.click()
                        except NoSuchAttributeException as error:
                            print("ERROR: {}".format(error))
                            self.found = True
                            break
                        links = self.driver.find_elements_by_css_selector('''div[id= 'search-page'] div[id = 'search-results'] main[class = 'search-results-list'] \
                                                                         article[class = 'result'] div[class = 'result-info'] h3[class = 'result-title'] a''')
                downloadLinks = WebDriverWait(self.driver, 15).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '''article[class = 'video-file'] div[class ='video-plain'] 
                                                                                                div[class = 'video-download'] p a''')))
                print(len(downloadLinks))
                for index in range(3, 5):
                    fileLink.append(downloadLinks[index].get_attribute('href'))
            except IndexError as error:
                self.driver.quit()
                videoDownloadErrors.put(error)
                raise
            except ElementClickInterceptedException as error:
                self.driver.quit()
                videoDownloadErrors.put(error)
                raise
            except TimeoutException as error:
                self.driver.quit()
                videoDownloadErrors.put(error)
                raise
            except NoSuchElementException as error:
                self.driver.quit()
                videoDownloadErrors.put(error)
                raise
            except WebDriverException as error:
                self.driver.quit()
                videoDownloadErrors.put(error)
                raise
            finally:
                self.driver.quit()
                return fileLink[0], fileLink[1]