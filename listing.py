import json

# Colorama module: pip install colorama
from colorama import init, Fore, Style

# Selenium module imports: pip install selenium
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as WDW
from selenium.common.exceptions import TimeoutException as TE
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

# Webdriver Manager module: pip install webdriver-manager
from webdriver_manager.chrome import ChromeDriverManager as CDM

# Python default imports.
from datetime import datetime as dt
from glob import glob
import os
from time import sleep

from os.path import exists

"""Colorama module constants."""
# This module may not work under MacOS.
init(convert=True, autoreset=True)  # Init the Colorama module.
red = Fore.RED  # Red color.
green = Fore.GREEN  # Green color.
yellow = Fore.YELLOW  # Yellow color.
reset = Style.RESET_ALL  # Reset color attribute.


class Reader:
    """Read files and extract NFTs data. Convert all types into a list."""

    def __init__(self, path: str) -> None:
        """Basically open a file and get all NFTs' data."""
        # Get file's extension to lowercase (MacOS support).
        self.path = path  # Instance the file path.
        # Get splitted file name (['text', '.txt']) and then remove the dot.
        self.extension = os.path.splitext(self.path)[1][1:].lower()
        # Check if the extension is supported by the Reader class.
        if self.extension in ('json', 'csv', 'xlsx'):
            # Eval function: self.extract_{FILE_EXTENSION}_file()
            eval(f'self.extract_{self.extension}_file()')
            print(self.file)
        else:  # Stop running the script.
            exit('The file extension is not supported.')

    def extract_json_file(self) -> None:
        """Transform JSON file format to a list of dictionaries."""
        from json import loads  # A Python default import.
        # Load and read the JSON file and extract "nft" part.
        self.file = loads(open(self.path, encoding='utf-8').read())['nft']
        self.lenght_file = len(self.file)  # Number of NFTs.

    def extract_csv_file(self) -> None:
        """Transform CSV file format to a list of dictionaries."""
        # Open file and splitlines (every "\n") and remove headers.
        # It gets a list of each rows.
        self.file = open(self.path, encoding='utf-8').read().splitlines()[1:]
        self.lenght_file = len(self.file)  # Number of NFTs.

    def extract_xlsx_file(self) -> None:
        """Transform XLSX file format to a dictionnary {key: {value, ...}}."""
        from pandas import read_excel  # Pandas module: pip install pandas
        self.file = read_excel(self.path)  # Read the Excel (XLSX) file.
        self.lenght_file = self.file.shape[0]  # Get number of rows.
        self.file = self.file.to_dict()  # Transform XLSX to a dictionnnary.


class Structure:
    """Structure JSON/CSV/XLSX data lists or dictionnaries."""

    def __init__(self, action: list) -> None:
        """Make a copy of the readed file and its extension."""
        self.file = reader.file.copy()  # File data copy.
        self.extension = reader.extension  # File extension copy.
        self.action = action  # 1, 2 or 1 and 2.
        if 1 in self.action and 2 not in self.action:
            from uuid import uuid4  # A Python default import.
            self.save_file = f'data/{str(uuid4())[:8]}.csv'
            with open(self.save_file, 'a+', encoding='utf-8') as file:
                file.write('nft_url;; supply;; blockchain;; type;; price;; '
                           'method;; duration;; specific_buyer;; quantity')

    def get_data(self, nft_number: int) -> None:
        """Get NFT's data."""
        self.nft_number = nft_number
        # Eval function: self.structure_{FILE_EXTENSION}()
        eval(f'self.structure_{self.extension}()')

    def structure_json(self) -> None:
        """Transform JSON dictionnaries list to a whole list."""
        nft_data = self.file[self.nft_number]  # Get datas of index.
        # Get key's value from the NFT data.
        nft_data = [nft_data[data] for data in nft_data]
        # Take each element in the list and check it.
        self.structure_data([self.dict_to_list(
            element) for element in nft_data])  # Then structure data.

    def structure_csv(self) -> None:
        """Transform CSV file into a list."""
        # Note: each information is split every ";;", you can change the
        self.structure_data(self.change_type(  # characters to others.
            self.file[self.nft_number].split(';;')))

    def structure_xlsx(self) -> None:
        """Transform XLSX file into a list."""
        self.structure_data([
            element.replace('nan', '').strip() if isinstance(element, str) else
            element for element in self.change_type([self.file[element].get(
                self.nft_number) for element in self.file])])

    def dict_to_list(self, element: dict or str) -> list or str:
        """Transform a dictionnary into a list. - JSON file method."""
        if isinstance(element, list):  # If element is a list.
            final_list = []  # Final list that will be return.
            for item in element:  # For each item in this list.
                temp_list = []  # Store all key's value.
                if isinstance(item, dict):  # If element is a dict.
                    # For each key in dict (item), get key's value.
                    [temp_list.append(item.get(key)) for key in item]
                else:
                    temp_list = item  # Do nothing.
                final_list.append(temp_list)  # Append the temp list.
            return final_list
        else:
            return element  # Return the same element.

    def change_type(self, nft_data: list) -> list:
        """Change type of element with a literal eval."""
        from ast import literal_eval  # A Python default import.
        list_ = []  # List that contains NFT's data.
        for data in nft_data:  # Get each element of NFT's data.
            element = str(data).strip()  # Remove whitespaces.
            try:  # Change type of element (str to int/float/list/bool).
                # In case of element is an integer, float, list or boolean.
                list_.append(literal_eval(element))
            except Exception:  # SyntaxError or ValueError.
                # In case of element is a real string.
                list_.append(element)
        return list_

    def structure_data(self, nft_data: list) -> None:
        """Structure each data of the NFT in a variable."""
        # self.nft_data_list = nft_data  # For development.
        #if 1 in self.action:  # Upload part.
        self.file_path: str or list = nft_data[0]
        self.nft_name: str = str(nft_data[1])  # Set string value to
        self.link: str = str(nft_data[2])  # real string to prevent
        self.description: str = str(nft_data[3])  # different types.
        self.collection: str = str(nft_data[4])
        self.properties: list = nft_data[5]  # [[type, name], ...].
        self.levels: list = nft_data[6]  # [[name, from, to], ...].
        self.stats: list = nft_data[7]  # [[name, from, to], ...].
        self.unlockable_content: list or bool = nft_data[8]  # [bool, str].
        self.explicit_and_sensitive_content: bool = nft_data[9]
        self.supply: int = nft_data[10]
        self.blockchain: str = str(nft_data[11]).capitalize()
        self.price: float or int = nft_data[12]
        self.quantity: int = nft_data[13]
        self.type: ""
        self.method: ""
        self.duration: list = ["1 month"]
        #self.duration: list = ["16-02-2022 14:00", "16-04-2022 15:00"]

    def is_empty(self, element: str, data: str, value: str = '') -> bool:
        """Check if data is empty and input its value."""
        if data != value:  # Check if the data is not an empty string
            web.send_keys(element, data)  # or a default value, and send it.
            return False
        return True

    def save_nft(self, url) -> None:
        """Save the NFT URL, Blockchain and supply number in a file."""
        # Note: only CSV file will be created.
        with open(self.save_file, 'a+', encoding='utf-8') as file:
            file.write(f'\n{url};; {self.supply};; {self.blockchain};;'
                       ' ;; ;; ;; ;; ;;')  # Complete data manually.
        print(f'{green}Data saved in {self.save_file}')


class Webdriver:
    """Webdriver class and methods to prevent exceptions."""

    def __init__(self) -> None:
        """Contains the file paths of the webdriver and the extension."""
        # Used files path, change them with your path if necessary.
        self.metamask_extension_path = os.path.abspath('assets/MetaMask.crx')
        self.driver = self.webdriver()  # Start new webdriver.

    def webdriver(self) -> webdriver:
        """Start a webdriver and return its state."""
        options = webdriver.ChromeOptions()  # Configure options for Chrome.
        options.add_extension(self.metamask_extension_path)  # Add extension.
        options.add_argument("log-level=3")  # No logs is printed.
        options.add_argument("--mute-audio")  # Audio is muted.
        options.add_argument("--lang=en-US")  # Set webdriver language
        options.add_experimental_option(  # to English. - 2 methods.
            'prefs', {'intl.accept_languages': 'en,en_US'})
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
#         driver = webdriver.Chrome(service=Service(  # DeprecationWarning using
#             CDM(log_level=0).install()), options=options)  # executable_path.
        os.environ['WDM_LOG_LEVEL'] = '0'
        driver = webdriver.Chrome(service=Service(  # DeprecationWarning using
                    CDM().install()), options=options)  # executable_path.
        driver.maximize_window()  # Maximize window to reach all elements.
        return driver

    def clickable(self, element: str) -> None:
        """Click on an element if it's clickable using Selenium."""
        try:
            WDW(self.driver, 5).until(EC.element_to_be_clickable(
                (By.XPATH, element))).click()
        except Exception:  # Some buttons need to be visible to be clickable,
            self.driver.execute_script(  # so JavaScript can bypass this.
                'arguments[0].click();', self.visible(element))

    def visible(self, element: str):
        """Check if an element is visible using Selenium."""
        return WDW(self.driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, element)))

    def send_keys(self, element: str, keys: str) -> None:
        """Send keys to an element if it's visible using Selenium."""
        try:
            self.visible(element).send_keys(keys)
        except Exception:  # Some elements are not visible but are present.
            WDW(self.driver, 5).until(EC.presence_of_element_located(
                (By.XPATH, element))).send_keys(keys)

    def send_date(self, element: str, keys: str) -> None:
        """Send a date (DD-MM-YYYY HH:MM) to a date input by clicking on it."""
        keys = keys.split('-') if '-' in keys else [keys]
        keys = [keys[1], keys[0], keys[2]] if len(keys) > 1 else keys
        for part in range(len(keys) - 1 if keys[len(keys) - 1]  # Compare years
                          == str(dt.now().year) else len(keys)):  # for clicks.
            self.clickable(element)  # Click first on the element.
            self.send_keys(element, keys[part])  # Then send it the date.

    def clear_text(self, element) -> None:
        """Clear text from an input."""
        self.clickable(element)  # Click on the element then clear its text.
        # Note: change with 'darwin' if it's not working on MacOS.
        control = Keys.COMMAND if os.name == 'posix' else Keys.CONTROL
        webdriver.ActionChains(self.driver).key_down(control).perform()
        webdriver.ActionChains(self.driver).send_keys('a').perform()
        webdriver.ActionChains(self.driver).key_up(control).perform()

    def window_handles(self, window_number: int) -> None:
        """Check for window handles and wait until a specific tab is opened."""
        WDW(self.driver, 30).until(lambda _: len(
            self.driver.window_handles) > window_number)
        # Switch to the asked tab.
        self.driver.switch_to.window(self.driver.window_handles[window_number])


class Wallets:
    """Allows connection to OpenSea with different wallets."""

    def __init__(self, wallet: int, password: int,
                         recovery_phrase: str) -> None:
        """Get the wallet and connect to the extension/etc."""
        self.recovery_phrase = recovery_phrase  # Get the phrase.
        self.password = password  # Get the new/same password.
        self.wallet = wallet.lower().replace(' ', '_')  # Wallet user choice.
        self.fails = 0  # Counter of fails during wallet connection.

    def login(self) -> bool:
        """Connect to OpenSea using a specific wallet."""
        return eval(f'self.{self.wallet}_login()')

    def contract(self) -> None:
        """Use the method of the wallet to sign the contract."""
        eval(f'self.{self.wallet}_contract()')

    def metamask_login(self) -> None:
        """Login to the MetaMask extension."""
        try:  # Try to login to the MetaMask extension.
            print('Login to MetaMask.', end=' ')
            web.window_handles(0)  # Switch to the MetaMask extension tab.
            web.driver.refresh()  # Reload the page to prevent a blank page.
            # Click on the "Start" button.
            web.clickable('//*[@class="welcome-page"]/button')
            # Click on the "Import wallet" button.
            web.clickable('//*[contains(@class, "btn-primary")][position()=1]')
            # Click on the "I agree" button.
            web.clickable('//footer/button[2]')
            # Input the recovery phrase.
            web.send_keys('//input[position()=1]', self.recovery_phrase)
            # Input a new password or the same password of your account.
            web.send_keys('//*[@id="password"]', self.password)
            web.send_keys('//*[@id="confirm-password"]', self.password)
            # Click on the "I have read and agree to the..." checkbox.
            web.clickable('(//*[@role="checkbox"])[2]')
            # Click on the "Import" button.
            web.clickable('//*[contains(@class, "btn-primary")][position()=1]')
            # Wait until the login worked and click on the "All done" button".
            web.visible('//*[contains(@class, "emoji")][position()=1]')
            web.clickable('//*[contains(@class, "btn-primary")][position()=1]')
            print(f'{green}Logged to MetaMask.{reset}')
        except Exception:  # Failed - a web element is not accessible.
            self.fails += 1  # Increment the counter.
            if self.fails < 2:  # Retry login to the wallet.
                print(f'{red}Login to MetaMask failed. Retrying.{reset}')
                self.metamask_login()
            else:  # Too many fails.
                self.fails = 0  # Reset the counter.
                print(f'{red}Login to MetaMask failed. Restarting.{reset}')
                web.driver.quit()  # Stop the webdriver.
                return False

    def metamask_contract(self) -> None:
        """Sign a MetaMask contract to login to OpenSea."""
        # Click on the "Sign" button - Make a contract link.
        # TODO: check
        web.clickable('//*[contains(@class, "button btn-secondary")]') # TODO: REQUIRED FOR LOGIN BUT CAN NOT WORK FOR SELL with POLYGON SO SEE BELOW NEW METHOD
        try:  # Wait until the MetaMask pop up is closed.
            WDW(web.driver, 10).until(EC.number_of_windows_to_be(2))
        except TE:
            self.metamask_contract()  # Sign the contract a second time.
        web.window_handles(1)  # Switch back to the OpenSea tab.

    def metamask_contract_polygon(self) -> None:
        """Sign a MetaMask contract to login to OpenSea."""

        #import pdb; pdb.set_trace()

        # Metamask pop up re-opens
        sleep(3)
        web.window_handles(2)
        # Scroll to btn
        web.visible('//*[contains(@class, "button btn-primary")]').location_once_scrolled_into_view
        # "Approve" network
        web.clickable('//*[contains(@class, "button btn-primary")]')

#         sleep(1)
#
#         # Do "Switch"
#         web.clickable('//*[contains(@class, "button btn-primary")]')
#
#         # Metamask pop up re-opens
#         sleep(3)
#         web.window_handles(2)
#
#         # Scroll to Sign btn
#         web.visible('//*[contains(@class, "button btn-primary")]').location_once_scrolled_into_view
#
#         sleep(1)
#         # Click on the "Sign" button - Make a contract link.
#         web.clickable('//*[contains(@class, "button btn-primary")]')

        try:  # Wait until the MetaMask pop up is closed.
            # TODO: MAKE LONGER IF TOO FAST
            # TODO: MAKE LONGER IF TOO FAST
            # TODO: MAKE LONGER IF TOO FAST
            # HACK to sign again and again until all signed
            WDW(web.driver, 3).until(EC.number_of_windows_to_be(2))
        except TE:
            #self.metamask_contract()  # Sign the contract a second time.
            # OR just repeat until sign is needed
            # but do it ONLY if error caught (popup is not closed - not finally signed)
            # otherwise it will SUccesfully pss sign step WITHUO making redundant attempt to sign again so it doestn fail if all good already (signed)
            self.metamask_contract_polygon()
        web.window_handles(1)  # Switch back to the OpenSea tab.


class OpenSea:
    """Main class: OpenSea automatic uploader."""

    def __init__(self) -> None:
        """Get the password and the recovery_phrase from the text file."""
        self.login_url = 'https://opensea.io/login?referrer=%2Fasset%2Fcreate'
        self.create_url = 'https://opensea.io/asset/create'  # OpenSea URLs.
        self.fails = 0  # Counter of fails during wallet connection.

    def login(self) -> None:
        """Login to OpenSea using MetaMask."""
        try:  # Try to login to the OpenSea using MetaMask.
            print('Login to OpenSea.', end=' ')
            web.window_handles(1)  # Switch to the main (data:,) tab.
            web.driver.get(self.login_url)  # Go to the OpenSea login URL.
            # Click on the "Show more options" button.
            web.clickable('//button[contains(@class, "show-more")]')
            # Click on the "MetaMask" button in list of wallets.
            web.clickable('//*[contains(text(), "MetaMask")]/../..')

            sleep(1)
            web.window_handles(2)  # Switch to the MetaMask pop up tab.

            sleep(1)
            # Click on the "Next" button.
            web.clickable('//*[@class="button btn-primary"]')

            sleep(1)
            # Click on the "Connect" button.
            web.clickable('//*[contains(@class, "button btn-primary")]')

            #WDW(web.driver, 5).until(EC.number_of_windows_to_be(1))
            #WDW(web.driver, 5).until(EC.number_of_windows_to_be(2))

            # It can be enough to login actually
            # but can be different if it is used in different cases
            # (not just login but listing with contract signing)

            # had to add focus to 1 window again and click meta wallet again - (hm, not always though)

            #web.window_handles(1)
            #web.clickable('//*[contains(text(), "MetaMask")]/../..')

            sleep(3)
            #import pdb; pdb.set_trace()
            web.window_handles(2)  # Switch to the MetaMask pop up tab.
            wallet.contract()  # Sign the contract.

            # Check if the login worked.
            WDW(web.driver, 15).until(EC.url_to_be(self.create_url))
            print(f'{green}Logged to OpenSea.{reset}\n')
        except Exception:  # The contract failed.
            try:
                web.window_handles(1)  # Switch back to the OpenSea tab.

                sleep(1)

                # likely also needed
                web.clickable('//*[contains(text(), "MetaMask")]/../..')

                sleep(1)
                web.window_handles(2)  # Switch to the MetaMask pop up tab.
                wallet.contract()  # Sign the contract.
                # Check if the login worked.
                WDW(web.driver, 15).until(EC.url_to_be(self.create_url))
                print(f'{green}Logged to OpenSea.{reset}\n')
            except Exception:
                self.fails += 1  # Increment the counter.
                if self.fails < 2:  # Retry login to the wallet.
                    print(f'{red}Login to OpenSea failed. Retrying.{reset}')
                    # Reload the page (is the login failed?).
                    web.driver.refresh()
                    self.login()  # Retry everything.
                else:  # Too many fails.
                    self.fails = 0  # Reset the counter.
                    print(f'{red}Login to OpenSea failed. Restarting.{reset}')
                    web.driver.quit()  # Stop the webdriver.
                    return False

    def upload(self, number: int) -> bool:
        """Upload multiple NFTs automatically on OpenSea."""
        print(f'Uploading NFT {number}/{reader.lenght_file}.', end=' ')
        try:  # Go to the OpenSea create URL and input all datas of the NFT.
            web.driver.get(self.create_url + '?enable_supply=true')
            if isinstance(structure.file_path, list):
                if len(structure.file_path) == 2:
                    file_path = os.path.abspath(structure.file_path[0])
                    preview = os.path.abspath(structure.file_path[1])
            else:  # No preview file.
                file_path = os.path.abspath(structure.file_path)
            if not os.path.exists(file_path):  # Upload the NFT file.
                raise TE('File doesn\'t exist or path is incorrect.')
            if os.path.getsize(file_path) / (1024 ** 2) > 100:
                raise TE('File size must be less than 100 MegaBytes.')
            if os.path.splitext(file_path)[1][1:].lower() not in \
                ('jpg', 'jpeg', 'png', 'gif', 'svg', 'mp4',  # Check the file
                 'webm', 'mp3', 'wav', 'ogg', 'glb', 'gltf'):  # extensions.
                raise TE('The file extension is not supported on OpenSea.')
            structure.is_empty('//*[@id="media"]', file_path)
            if os.path.splitext(file_path)[1][1:].lower() in \
                    ('mp4', 'webm', 'mp3', 'wav', 'ogg', 'glb', 'gltf'):
                if not os.path.exists(preview):  # Upload the NFT file.
                    raise TE('File doesn\'t exist or path is incorrect.')
                if os.path.getsize(preview) / (1024 ** 2) > 100:
                    raise TE('File size must be less than 100 MegaBytes.')
                structure.is_empty('//input[@name="preview"]', preview)
            # Input NFT name.
            if structure.is_empty('//*[@id="name"]', structure.nft_name):
                raise TE('The NFT name is missing.')
            # Input external link.
            structure.is_empty('//*[@id="external_link"]', structure.link)
            # Input description.
            structure.is_empty('//*[@id="description"]', structure.description)
            if not structure.is_empty(  # Input collection and select it.
                    '//form/div[5]/div/div[2]/input', structure.collection):
                try:  # Try to click on the collection button.
                    collection = ('//span[contains(text(), "'
                                  f'{structure.collection}")]/../..')
                    web.visible(collection)  # Check that the collection span
                    web.clickable(collection)  # is visible and click on it.
                except Exception:  # If collection doesn't exist.
                    raise TE('Collection doesn\'t exist or can\'t be found.')
            datas = [structure.properties, structure.levels, structure.stats]
            for index in range(len(datas)):  # Add properties, levels & stats.
                if not len(datas[index]) > 0:  # Check if data is not empty.
                    continue  # Pass this data because it's empty or null.
                # Change element from a list of strings to a list of lists.
                if not isinstance(datas[index][0], list):
                    datas[index] = [datas[index]]  # Target maybe useless.
                web.clickable(  # Click on "+" button to open the pop up.
                    f'//form/section/div[{index + 1}]/div/div[2]/button')
                number_ = 0
                for data in datas[index]:
                    if number_ > 0:  # If there are more than 1 element.
                        # Click on "Add more" button.
                        web.clickable('//div[@role="dialog"]/section/button')
                    number_ += 1  # Increase number to add more element.
                    web.send_keys(  # Input values in the inputs.
                        f'/html/body/div[{index + 2}]/div/div/div/section/tabl'
                        f'e/tbody/tr[{number_}]/td[1]/div/div/input', data[0])
                    for rank in [3, 2]:  # Input third and second values.
                        if len(data) == 3 or rank == 2:  # 1 or 2 loops.
                            actual_element = f'/html/body/div[{index + 2}]' + \
                                '/div/div/div/section/table/tbody/' + \
                                f'tr[{number_}]/td[{rank}]/div/div/input'
                            web.clear_text(actual_element)  # Default text.
                            web.send_keys(actual_element, data[rank - 1])
                web.clickable('//footer/button')  # Click on the "Save" button.
            # Click on the "Unlockable Content" switch if it's true.
            if isinstance(structure.unlockable_content, list):  # If not False.
                if len(structure.unlockable_content) > 0:  # Not an empty list.
                    if isinstance(structure.unlockable_content[0], bool):
                        if structure.unlockable_content[0]:  # If True.
                            web.send_keys('//*[@id="unlockable-content-toggle'
                                          '"]', Keys.ENTER)  # Toggle button.
                            web.send_keys(  # Input the unlockable content.
                                '//div[contains(@class, "unlockable")]/'
                                'textarea', structure.unlockable_content[1])
            # Click on the "Explicit & Sensitive Content" switch if it's true.
            if structure.explicit_and_sensitive_content != '':  # Not empty.
                if isinstance(structure.explicit_and_sensitive_content, bool):
                    if structure.explicit_and_sensitive_content:  # True.
                        web.send_keys('//*[@id="explicit-content-toggle"]',
                                      Keys.ENTER)  # Toggle button.
            # Set number of supplies if it's not an empty string.
            if structure.supply != '' and 'supply=' in web.driver.current_url:
                if isinstance(structure.supply, int):  # Integer.
                    if structure.supply > 1:  # Set supplies deleting default
                        web.send_keys('//*[@id="supply"]',  # supply (= 1).
                                      f'{Keys.BACKSPACE}{structure.supply}')
            else:  # This is important for the sale part.
                structure.supply = 1
            # Set Blockchain if it's different from "Ethereum".
            if structure.blockchain != '':  # If it's not an empty string.
                if web.visible('//*[@id="chain"]').get_attribute('value') \
                        != structure.blockchain:  # Compare to the span text.
                    try:  # Try to select the Blockchain.
                        web.clickable('//*[@id="chain"]/..')  # Open the sheet.
                        web.clickable('//span[contains(text(), '
                                      f'"{structure.blockchain}")]/../..')
                    except Exception:  # Blockchain is unknown.
                        raise TE('Blockchain is unknown or badly written.')
            else:  # This is important for the sale part.
                structure.blockchain = 'Ethereum'
            web.clickable('(//div[contains(@class, "submit")])'  # Click on the
                          '[position()=1]/div/span/button')  # "Create" button.
            WDW(web.driver, 30).until(lambda _: web.driver.current_url !=
                                      self.create_url + '?enable_supply=true')
            sleep(20)
            print(f'{green}NFT uploaded.{reset}')
            if 2 not in structure.action:  # Save the data for future upload.
                structure.save_nft(web.driver.current_url)
            return True  # If it perfectly worked.
        except Exception as error:  # An element is not reachable.
            print(f'{red}An error occured.{reset} {error}')
            return False  # If it failed.

    def sale(self, number: int, sell_url, quantity, price, duration, network, date: str = '%d-%m-%Y %H:%M') -> None:
        """Set a price for the NFT and sell it."""

        print(f'Sale of the NFT {number}')

        try:  # Try to sell the NFT with different types and methods.
            web.driver.get(sell_url)  # Sale page.

            #import pdb; pdb.set_trace()

            web.send_keys('//*[@name="price"]', format(price, '.8f'))
            if web.visible('//*[@id="duration"]/div[2]').text \
                    != duration:  # Not default.
                web.clickable('//*[@id="duration"]')  # Date button.
                web.clickable('//*[@role="dialog"]'  # Duration Range
                              '/div[1]/div/div[2]/input')  # sheet.
                web.clickable('//span[contains(text(), '   # Date span.
                              f'"{duration}")]/../..')
                web.send_keys('//*[@role="dialog"]', Keys.ENTER)

            sleep(2)
            #import pdb; pdb.set_trace()
            # WDW(web.driver, 3).until(EC.number_of_windows_to_be(2))

            try:  # Click on the "Complete listing" (submit) button.
                web.clickable('//button[@type="submit"]')
                #sleep(2)
            except Exception:  # An unknown error has occured.
                raise TE('The submit button cannot be clicked.')
            try:  # Polygon blockchain requires a click on a button.
                if network == 'Polygon':
                    web.window_handles(2)
                    wallet.metamask_contract_polygon()
                else:
                    web.window_handles(2)  # Switch to the MetaMask pop up tab.
                    wallet.contract()  # Sign the contract.
            except Exception:  # No deposit or an unknown error occured.
                log_failed_listing(number)
                raise TE('You (MAYBE) need to make a deposit before proceeding'
                         ' to listing of your NFTs.')
            web.window_handles(1)  # Switch back to the OpenSea tab.
            try:  # Wait until the NFT is listed.
                # TODO: TEST IT WORKS (previous condition might be is waiting for 2 windows but maybe it could be better)
                web.visible('//header/h4')  # "Your NFT is listed!".
                print(f'{green}NFT put up for sale.{reset}')
            except Exception:  # An error occured while listing the NFT.
                raise TE('The NFT is not listed.')
        except Exception as error:  # Failed, an error has occured.
            # Add json or something with failed id
            log_failed_listing(number)
            print(f'{red}NFT sale cancelled.{reset} {error}')


def choose_wallet() -> int:
    """Ask the user for a wallet to connect to OpenSea."""
    wallets = ['MetaMask']  # New wallets will be added.
    while True:
        print(f'{yellow}\nChoose a wallet:')
        [print(f'{wallets.index(wallet) + 1} - {wallet}'
               ) for wallet in wallets]  # Print wallets.
        answer = input('Wallet: ')  # Get the user answer.
        if not answer.isdigit():  # Check if answer is a number.
            print(f'{red}Answer must be an integer.')
        elif int(answer) > len(wallets) or int(answer) <= 0:
            print(f'{red}Wallet doesn\'t exist.')
        else:  # Return the name of wallet with a function format.
            return wallets[int(answer) - 1].lower().replace(' ', '_')


def read_file(file_: str, question: str) -> str:
    """Read file or ask for data to write in text file."""
    if not os.path.isfile(f'assets/{file_}.txt'):
        open(f'assets/{file_}.txt', 'a')  # Create a file if it doesn't exist.
    with open(f'assets/{file_}.txt', 'r+', encoding='utf-8') as file:
        text = file.read()  # Read the file.
        if text == '':  # If the file is empty.
            text = input(question)  # Ask the question.
            if input(f'Do you want to save your {file_} in '
                     'a text file? (y/n) ').lower() != 'y':
                print(f'{yellow}Not saved.{reset}')
            else:
                file.write(text)  # Write the text in file.
                print(f'{green}Saved.{reset}')
        return text

def data_file() -> str:
    """Read the data folder and extract JSON, CSV and XLSX files."""
    while True:
        file_number, files_list = 0, []
        print(f'{yellow}\nChoose your file:{reset}\n0 - Browse a file on PC.')
        for files in [glob(f'data/{extension}')  # Files of the data folder.
                      for extension in ['*.json', '*.csv', '*.xlsx']]:
            for file in files:
                file_number += 1
                files_list.append(file)
                print(f'{file_number} - {os.path.abspath(file)}')
        answer = input('File number: ')
        cls()  # Clear console.
        if not answer.isdigit():  # Check if answer is a number.
            print(f'{red}Answer must be an integer.{reset}')
        elif int(answer) == 0:  # Browse a file on PC.
            print(f'{yellow}Browsing on your computer...{reset}')
            from tkinter import Tk  # Tkinter module: pip install tk
            from tkinter.filedialog import askopenfilename
            Tk().withdraw()  # Hide Tkinter tab.
            return askopenfilename(filetypes=[('', '.json .csv .xlsx')])
        elif int(answer) <= len(files_list):
            return files_list[int(answer) - 1]  # Return path of file.
        print(f'{red}File doesn\'t exist.{reset}')


def cls() -> None:
    """Clear console function."""
    # Clear console for Windows using 'cls' and Linux & Mac using 'clear'.
    os.system('cls' if os.name == 'nt' else 'clear')

# Test logging failes/useful info
def log_failed_listing(id: int) -> None:
    file_name = 'listing_failed.json'
    json_object = {}

    if exists(file_name):
        with open(file_name, 'r') as openfile:
            # Reading from json file
            json_object = json.load(openfile)

    #print(json_object)

    # Modify
    if str(id) not in json_object:
        json_object[id] = 'failed'

    json_dump = json.dumps(json_object, indent=2)

    # Writing json
    with open(file_name, "w") as outfile:
        outfile.write(json_dump)


if __name__ == '__main__':
    cls()  # Clear console.

    # Test logging failes/useful info
    # log_failed_listing(3)

    wallet = Wallets('MetaMask',  # Send the password / recovery phrase.
        read_file('password', '\nWhat is your MetaMask password? '), read_file(
            'recovery_phrase', '\nWhat is your MetaMask recovery phrase? '))

    action = [1]
    web = Webdriver()  # Start a new webdriver and init its methods.
    opensea = OpenSea()  # Init the OpenSea class.

    wallet.login()  # Connect to MetaMask.
    opensea.login()  # Connect to OpenSea.

    #### REQUIRED PARAMS
    network = 'Polygon'
    # Test collection
    #collection_url = 'https://opensea.io/assets/matic/0x2b62d10e62fe1065537301ff1b24912495ff18ed'
    # Real collection
    collection_url = 'https://opensea.io/assets/matic/0x844e78ffc63447087c5d7cde41fddf4b54f6b2d7'
    quantity = 1
    price = 0.01
    duration = '6 months'



    # SAVE LISTED SOMEWHERE
    start = 1
    stop = 1

#     start_stop = 9
#     start = start_stop
#     stop = start_stop

    for nft_number in range(start, stop + 1):
        sell_url = collection_url + f'/{nft_number}/sell'
        opensea.sale(nft_number, sell_url, quantity, price, duration, network) # Sell NFT.
        #web.driver.quit()  # Stop the webdriver.
    print(f'\n{green}All done! (Check failed in listing_failed.json).{reset}')




#     # Failed flow - COPY FROM listing_failed.json and CLEAN listing_failed.json before starting (to see if failed again)
#     failed = [793]
#
#     for nft_number in failed:
#         sell_url = collection_url + f'/{nft_number}/sell'
#         opensea.sale(nft_number, sell_url, quantity, price, duration, network) # Sell NFT.
#        #web.driver.quit()  # Stop the webdriver.
#     print(f'\n{green}All done! (Check failed in listing_failed.json).{reset}')
