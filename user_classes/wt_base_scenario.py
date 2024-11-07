from locust import task, SequentialTaskSet, FastHttpUser, HttpUser, constant_pacing, events
from config.config import cfg, logger
from utils.assertion import check_http_response
from utils.non_test_methods import open_csv_file
import sys, re, random

class PurchaseFlightTicket(SequentialTaskSet): # класс с задачами (содержит основной сценарий)

    test_users_csv_filepath = './test_data/user_creds.csv' 

    def on_start(self):
        
        @task()
        def uc00_getHomePage(self) -> None:
            self.test_users_data = open_csv_file(self.test_users_csv_filepath)
            logger.info(f"Test data for users is: {self.test_users_data}")

           
            r00_0_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7', 
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-language': 'ru',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': 'localhost:1080',
            'Sec-Fetch-Dest': 'frame',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'sec-fetch-user': '?1',
            'Upgrade-Insecure-Requests': '1'   
            }
                    
            self.client.get(
                '/WebTours/',
                name="req_00_0_getHomePage_/WebTours/",
                allow_redirects=False,
            #debug_stream=sys.stderr
            )        

            self.client.get(
                '/WebTours/header.html',
                name="req_00_1_getHomePage_/WebTours/header.html",
                allow_redirects=False,
            #debug_stream=sys.stderr
            )

            r_02_url_param_signOff = 'true' 

            self.client.get(
                f'/cgi-bin/welcome.pl?signOff={r_02_url_param_signOff}',
                name="req_00_2_getHomePage_cgi-bin/welcome.pl?signOff",
                allow_redirects=False,
            #debug_stream=sys.stderr
            )

            with self.client.get(
                f'/cgi-bin/nav.pl?in=home',
                name="req_00_3_getHomePage_cgi-bin/nav.pl?in=home",
                allow_redirects=False,
                catch_response=True
            #debug_stream=sys.stderr,
            ) as req00_3_response:
                check_http_response(req00_3_response, 'name="userSession"')
            # print(f"\n__\n req_00_3 response text: {req00_3_response.text}\n__\n")

            self.user_session = re.search(r"name=\"userSession\" value=\"(.*)\"/>", req00_3_response.text).group(1)

            logger.info(f"USER_SESSION_PARAMETR: {self.user_session}")

            self.client.get(
                f'/WebTours/home.html',
                name="req_00_4_getHomePage_WebTours/home.html",
                allow_redirects=False,
            #debug_stream=sys.stderr
            )

        @task()
        def uc01_LoginAction(self) -> None:
            r01_00_headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            self.user_data_row = random.choice(self.test_users_data)
            logger.info(self.user_data_row)


            self.username = self.user_data_row["username"]
            self.password = self.user_data_row["password"]

            logger.info(f"chosen username: {self.username} / password: {self.password}")

            r01_00_body = f"userSession={self.user_session}&username={self.username}&password={self.password}&login.x=49&login.y=8&JSFormSubmit=off"

            with self.client.post(
                '/cgi-bin/login.pl',
                name='req_01_0_LoginAction_/cgi-bin/login.pl',
                headers=r01_00_headers,
                data=r01_00_body,
                debug_stream=sys.stderr,
                catch_response=True
            )as r_01_00response:
                check_http_response(r_01_00response, "User password was correct")

            self.client.post(
                '/cgi-bin/nav.pl?page=menu&in=home',
                name='req_01_1_LoginAction_/cgi-bin/nav.pl?page=menu&in=home',
                allow_redirects=False,
                #debug_stream=sys.stderr,
            )

            self.client.post(
                '/cgi-bin/login.pl?intro=true',
                name='req_01_2_LoginAction_/cgi-bin/login.pl?intro=true', 
                 allow_redirects=False,
                #debug_stream=sys.stderr,
            )
                 
        uc00_getHomePage(self)
        uc01_LoginAction(self)

    @task
    def my_dummy_task(self):
        print('ЧТО-ТО')    


class WebToursBaseUserClass(FastHttpUser): # юзер-класс, принимающий в себя основные параметры теста
    wait_time = constant_pacing(cfg.pasing)

    host = cfg.url

    logger.info(f'WebToursBaseUserClass started. Host: {host}')

    tasks = [PurchaseFlightTicket]