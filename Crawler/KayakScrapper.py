import datetime

import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import json
import csv
import uuid

nonstop_indexes = {
    "company": 1,
    "nonstop": 2,
    "duration": 3,
    "origin": 4,
    "destination": 6,
    "price": 9
}

stops_indexes = {
    "company": 1,
    "nonstop": 2,
    "duration": 4,
    "origin": 5,
    "destination": 7,
    "price": 10
}

now = datetime.datetime.now()
DESTINATION_PATH = r"E:\UBB\BigData\HadoopSharedFolder\flights.csv"
BACKUP_PATH = r"E:\UBB\BigData\ArchiveCrawls\flights-{}.csv".format(now.strftime("%Y-%m-%d-%H-%M-%S"))
def parse_kayak_text_string(text):
    split_fields = text.split(b"\n")
    decoded_fields = [ x.decode('utf-8') for x in split_fields]

    total_duration = None
    origin_airport = None
    destination_airport = None
    price = None
    is_lot = False

    for field in decoded_fields:
        if "$" in field:
            price = int(field[1:].replace(",", ""))

    if decoded_fields[0] == "Cheapest":
        pass
    elif decoded_fields[0] == "Best":
        pass
    else:
        non_stop = decoded_fields[2] == "nonstop"
        indexes = nonstop_indexes if non_stop else stops_indexes
        company = decoded_fields[1]
        if company == "LOT":
            is_lot = True

        try:
            duration = decoded_fields[indexes.get('duration')]

            hours, minutes = duration.split(" ")
            total_duration = int(minutes[:-1]) + (int(hours[:-1])*60)
        except:
            pass

        try:
            origin_airport = decoded_fields[indexes.get('origin')]
        except:
            pass

        try:
            destination_airport = decoded_fields[indexes.get('destination')]
        except:
            pass
        #price = decoded_fields[indexes.get('price') if not is_lot else indexes.get('price') + 1]

    return origin_airport, destination_airport, total_duration, price


class FlightInformation():
    def __init__(self, origin, destination, duration, price, departure_date=None, acquired_on=None):
        self.ID = uuid.uuid4()
        self.origin = origin
        self.destination = destination
        self.duration = duration
        self.departure_date = departure_date
        self.price = price
        self.acquired_on = acquired_on

    def to_dict(self):
        dict = {
            "ID": self.ID,
            "origin": self.origin,
            "destination": self.destination,
            "duration": self.duration,
            "departure_date": self.departure_date,
            "price": self.price,
            "acquired_on": self.acquired_on
        }
        return dict

    def set_departure_date(self, date):
        self.departure_date = date

    def set_acquisition_date(self, date):
        self.acquired_on = date

    @staticmethod
    def is_flight_information_complete(flight_info):
        attribute_list = ["ID", "origin", "destination", "duration", "price", "departure_date", "acquired_on"]
        for attr in attribute_list:
            try:
                attr_value = flight_info.__getattribute__(attr)
                if isinstance(attr_value, str) and flight_info == "":
                    return False
                elif attr_value is None:
                    return False
            except Exception as exc:
                print(exc)
                return False
        return True

    @staticmethod
    def create_flight_information_from_parser(text, parser):
        origin, destination, duration, price = parser(text)
        flight = FlightInformation(origin, destination, duration, price)
        return flight


from selenium.webdriver.chrome.options import Options
#chrome_options = Options()
#chrome_options.add_argument("--headless")
driver = webdriver.Chrome()#options=chrome_options)
url = "https://kayak.com/flights"
driver.get(url)
time.sleep(1)


LIST_ORIGIN_AIRPORTS = [
    "Cluj-Napoca",
    "Berlin",
    "Amsterdam",
    "Athens",
    "Belgrade",
    "Bern",
    "Bratislava",
    "Brussels",
    "Budapest",
    "Chisinau",
    "Copenhagen",
    "Dublin",
    "Helsinki",
    "Kiev",
    "Lisbon",
    "Luxembourg",
    "Madrid",
    "Minsk",
    "Moscow",
    "Nicosia",
    "Nuuk",
    "Oslo",
    "Paris",
    "Podgorica",
    "Prague",
    "Reykjavik",
    "Riga",
    "Rome",
    "Sarajevo",
    "Skopje",
    "Sofia",
    "Stockholm",
    "Tallinn",
    "Tirana",
    "Wien",
    "Vilnius",
    "Warsaw",
    "Zagreb"
]

now = datetime.datetime.now()
next_week = now + datetime.timedelta(days=7)
next_week_day_label = next_week.strftime("%A %B %d, %Y")

tab_index = 0

for origin_airport in LIST_ORIGIN_AIRPORTS:
    try:
        origin = driver.find_element(By.CLASS_NAME, "zEiP-origin")
        origin.click()
        remove_suggestion = driver.find_element(By.CSS_SELECTOR, "[aria-label='Remove']")
        remove_suggestion.click()
        time.sleep(0.5)
        flight_origin_text = driver.find_element(By.CSS_SELECTOR, "[aria-label='Flight origin input']")
        flight_origin_text.send_keys(origin_airport)
        time.sleep(1)
        flight_origin_text.send_keys(Keys.ENTER)
        time.sleep(0.5)
        flight_destination = driver.find_element(By.CSS_SELECTOR, "[aria-label='Flight destination input']")
        flight_destination.send_keys("London")
        time.sleep(1)
        flight_destination.send_keys(Keys.ENTER)
        time.sleep(0.5)
        one_way = driver.find_element(By.CSS_SELECTOR, "[aria-label='One-way']")
        one_way.click()
        time.sleep(0.5)

        start_date = driver.find_element(By.CSS_SELECTOR, "[aria-label='Start date calendar input']")
        start_date.click()
        time.sleep(0.5)

        prev_month = driver.find_element(By.CSS_SELECTOR, "[aria-label='Previous month']")
        prev_month.click()
        time.sleep(1)

        next_week_day_button = driver.find_element(By.CSS_SELECTOR, "[aria-label='{}']".format(next_week_day_label))
        next_week_day_button.click()
        time.sleep(1)

        search = driver.find_element(By.CSS_SELECTOR, "[aria-label='Search']")
        search.click()

        time.sleep(20)
        driver.switch_to.window(driver.window_handles[tab_index])
        results = driver.find_elements(By.CLASS_NAME, "Flights-Results-FlightResultItem")
        print("Got flight results: {}.".format(len(results)))
        current_time = datetime.datetime.now(datetime.timezone.utc)

        flights_json = []
        field_names = ["ID", 'origin', 'destination', 'duration', 'departure_date', 'price', "acquired_on"]
        with open(DESTINATION_PATH, "a+", newline='') as csvfile:
            csv_writer = csv.DictWriter(csvfile, fieldnames=field_names)
            for flight in results:
                print(bytes(flight.text, encoding='utf-8'))
                flight_obj = FlightInformation.create_flight_information_from_parser(bytes(flight.text, encoding='utf-8'),
                                                                                     parse_kayak_text_string)
                flight_obj.set_departure_date(next_week.strftime("%Y/%m/%d"))
                flight_obj.set_acquisition_date(current_time.strftime("%Y-%m-%d %H:%M:%S"))
                if FlightInformation.is_flight_information_complete(flight_obj):
                    csv_writer.writerow(flight_obj.to_dict())

        # with open("./flights", "a+") as handle:
        #     json.dump(flights_json, handle, indent=4)

        tab_index += 1
    except Exception as exc:
        print(f"[ERROR] EXCEPTION OCCURED: {exc}")
        chrome_options = Options()
        #chrome_options.add_argument("--headless")
        driver = webdriver.Chrome()#options=chrome_options)
        url = "https://kayak.com/flights"
        driver.get(url)
        tab_index = 0
        time.sleep(1)

import shutil
open(BACKUP_PATH, mode="w").close()
shutil.copy(DESTINATION_PATH, BACKUP_PATH)

