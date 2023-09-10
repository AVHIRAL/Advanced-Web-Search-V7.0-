import tkinter as tk
import tkinter.ttk as ttk
from tkinter import PhotoImage, IntVar, Checkbutton
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from googleapiclient.discovery import build
import googlesearch as gs
import webbrowser
import time
import winsound
import requests
import hashlib
import webbrowser

YOUR_API_KEY = 'AIzaSyBBmGey_szXrjgjPhGNqRJg1vTzEHMOieM'
YOUR_CSE_ID = 'b5b25e04945ea4cd1'

webdriver.chrome.service.Service.log_path = "chromedriver.log"

google_custom_search = build ("customsearch", "v1", developerKey=YOUR_API_KEY)


class AdvancedSearchApp:
    def __init__(self, root):
        # Initialisation de l'application
        self.root = root
        self.root.title ("Advanced Web Search Prospects - AVHIRAL V7.0")

        # Cadre supérieur contenant les éléments d'entrée et de bouton
        self.top_frame = tk.Frame (root)
        self.top_frame.pack (pady=10, fill='x')

        # Étiquette de mot-clé
        self.label = tk.Label (self.top_frame, text="Entrez un mot-clé:")
        self.label.pack (side='left')

        # Champ de saisie de mot-clé

        self.entry = tk.Entry (self.top_frame, width=70)
        self.entry.pack (side='left', padx=10)
        self.entry.bind ("<Return>", self.search_on_enter)

        # Cadre de paramètres pour les champs de saisie horizontaux
        self.params_frame = tk.Frame (root)
        self.params_frame.pack (anchor='w')

        # Étiquette et champ de saisie de secteur
        self.sector_label = tk.Label (self.params_frame, text="Secteur:")
        self.sector_label.pack (side='left', padx=10)
        self.sector_entry = tk.Entry (self.params_frame, width=20)
        self.sector_entry.pack (side='left', padx=10)

        # Étiquette et champ de saisie de localité
        self.location_label = tk.Label (self.params_frame, text="Localité:")
        self.location_label.pack (side='left', padx=10)
        self.location_entry = tk.Entry (self.params_frame, width=20)
        self.location_entry.pack (side='left', padx=10)

        # Étiquette et menu déroulant pour la sélection du genre
        self.gender_label = tk.Label (self.params_frame, text="Homme ou Femme:")
        self.gender_label.pack (side='left', padx=10)
        self.gender_var = tk.StringVar (root)
        self.gender_var.set ("Tout")  # Valeur par défaut
        self.gender_menu = ttk.Combobox (self.params_frame, textvariable=self.gender_var,
                                         values=["Tout", "Homme", "Femme"])
        self.gender_menu.pack (side='left', padx=10)

        # Étiquette et champ de saisie de société
        self.company_label = tk.Label (self.params_frame, text="Société:")
        self.company_label.pack (side='left', padx=10)
        self.company_entry = tk.Entry (self.params_frame, width=20)
        self.company_entry.pack (side='left', padx=10)

        # Case à cocher pour la recherche de liens invisibles
        self.invisible_links_var = tk.BooleanVar ( )
        self.invisible_links_checkbox = tk.Checkbutton (self.params_frame, text="Recherche de liens invisibles",
                                                        variable=self.invisible_links_var)
        self.invisible_links_checkbox.pack (side='left', padx=10)

        # Initialisation du cache
        self.cache = {}

        # Bouton de recherche
        self.button = tk.Button (self.top_frame, text="Rechercher", command=self.search)
        self.button.pack (side='left', padx=10)

        # Bouton de suppression
        self.clear_button = tk.Button (self.top_frame, text="Clear", command=self.clear_content)
        self.clear_button.pack (side='left', padx=10)

        # Indicateur visuel d'état
        self.led = tk.Label (self.top_frame, text="●", fg="green", font=("Arial", 16))
        self.led.pack (side='left', padx=5)

        # Zone de texte de résultats avec défilement
        self.scrollbar = tk.Scrollbar (root)
        self.results_text = tk.Text (root, wrap=tk.WORD, cursor="arrow", yscrollcommand=self.scrollbar.set)
        self.results_text.pack (expand=True, fill='both', side='left')
        self.scrollbar.pack (side='left', fill='y')
        self.scrollbar.config (command=self.results_text.yview)

        # Configuration des tags pour les liens
        self.results_text.tag_configure ("url_hover", foreground="darkblue", underline=True)
        self.results_text.tag_configure ("url", foreground="black")

        self.results = []
        self.current_index = 0

        # Ajout du logo AVHIRAL
        self.logo_image = PhotoImage (file="logo_avhiral.png")
        self.logo_label = tk.Label (root, image=self.logo_image)
        self.logo_label.pack (side="right", padx=20)
        self.logo_label.bind ('<Enter>', self.on_logo_enter)
        self.logo_label.bind ('<Leave>', self.on_logo_leave)
        self.logo_label.bind ('<Button-1>', self.open_avhiral_website)

        # Ajout du label "Recherche en cours..."
        self.status_label = tk.Label (self.top_frame, text="", foreground="red", font=("Arial", 12))
        self.status_label.pack (side='left', padx=10)
        self.root.after (1000, self.blink_status_label)

    def update_progress(self, percentage):
        self.progress_label.config (text=f"Progression : {percentage}%")

    def blink_status_label(self):
        current_text = self.status_label.cget ("text")
        if current_text:
            self.status_label.config (text="")
        else:
            self.status_label.config (text="")
        self.root.after (1000, self.blink_status_label)

    def search_on_enter(self, event):
        self.search ( )

    def clear_content(self):
        self.entry.delete (0, tk.END)  # Efface le contenu de l'entrée
        self.results_text.delete (1.0, tk.END)  # Efface le texte des résultats
        self.results = []  # Vide la liste des résultats
        self.current_index = 0  # Réinitialise l'index courant
        self.sector_entry.delete (0, tk.END)  # Efface le champ de secteur
        self.location_entry.delete (0, tk.END)  # Efface le champ de localité
        self.gender_var.set ("Tout")  # Réinitialise le menu déroulant du genre
        self.company_entry.delete (0, tk.END)  # Efface le champ de société

    def generate_search_key(self, keyword, sector, location, gender, company):
        # Utilisez hashlib pour créer une clé unique basée sur les paramètres de recherche
        search_key = hashlib.sha256 (f"{keyword}{sector}{location}{gender}{company}".encode ( )).hexdigest ( )
        return search_key

    def search(self):
        # Modifiez l'apparence du bouton pendant la recherche
        self.button.config (bg="red", text="Recherche en cours...")
        self.led.config (fg="red")
        self.status_label.config (text="Recherche en cours...")
        self.root.update ( )

        # Obtenez les paramètres de recherche
        keyword = self.entry.get ( )
        sector = self.sector_entry.get ( )
        location = self.location_entry.get ( )
        gender = self.gender_var.get ( )
        company = self.company_entry.get ( )

        # Clé unique basée sur les paramètres de recherche
        search_key = self.generate_search_key (keyword, sector, location, gender, company)

        # Vérifiez d'abord si les résultats existent déjà dans le cache
        if search_key in self.cache:
            # Utilisez les résultats du cache
            self.results = self.cache[search_key]
        else:
            # Effectuez la recherche en utilisant Google Custom Search
            self.results = []
            query = keyword + f" {sector} {location} {gender} {company}"
            try:
                # Utilisez l'API Google Custom Search pour obtenir les résultats
                google_results = google_custom_search.cse ( ).list (q=query, cx=YOUR_CSE_ID).execute ( )
                for item in google_results.get ('items', []):
                    self.results.append (item['link'])
            except Exception as e:
                print ("Erreur lors de la recherche Google Custom Search:", e)

            # Effectuez également une recherche en utilisant googlesearch-python comme auparavant
            for result in gs.search (query, lang='uk', stop=500):
                self.make_links_clickable (result)
                self.results.append (result)
                self.root.update_idletasks ( )
            self.led.config (fg="green")

        # Recherche de liens invisibles
        if self.invisible_links_var.get():
            invisible_results = self.search_invisible_links(self.results)
            for result in invisible_results:
                self.make_links_clickable(result)
                self.results.append(result)

        # Stockez les résultats dans le cache sous la clé appropriée
        self.cache[search_key] = self.results

        # Modifiez l'apparence du bouton pendant la recherche
        self.button.config (bg="red", text="Recherche en cours...")
        self.led.config (fg="red")
        self.status_label.config (text="Recherche en cours...")
        self.root.update ( )

        keyword = self.entry.get ( )
        sector = self.sector_entry.get ( )  # Obtenez la valeur du champ de secteur
        location = self.location_entry.get ( )  # Obtenez la valeur du champ de localité
        gender = self.gender_var.get ( )  # Obtenez la valeur du menu déroulant du genre
        company = self.company_entry.get ( )  # Obtenez la valeur du champ de société

        # Utilisez ces paramètres dans votre recherche
        for result in gs.search (keyword + f" {sector} {location} {gender} {company}", lang='uk', stop=500):
            self.make_links_clickable (result)
            self.results.append (result)
            self.root.update_idletasks ( )
        self.led.config (fg="green")
        winsound.Beep (2000, 300)

        # Rétablissez l'apparence du bouton après la recherche
        self.button.config (bg="SystemButtonFace", text="Rechercher")
        self.led.config (fg="green")
        self.status_label.config (text="")
        winsound.Beep (2000, 300)

        # Bing search
        for result in self.bing_search (keyword, 500):
            self.make_links_clickable (result)
            self.results.append (result)
            self.root.update_idletasks ( )

        # DuckDuckGo search
        for result in self.duckduckgo_search (keyword, 500):
            self.make_links_clickable (result)
            self.results.append (result)
            self.root.update_idletasks ( )

    def bing_search(self, query, num_results=10):
        headers = {"User-Agent": "Mozilla/5.0"}
        search_url = f"https://www.bing.com/search?q={query}"
        response = requests.get (search_url, headers=headers)
        soup = BeautifulSoup (response.text, "html.parser")
        results = [link.get ('href') for link in soup.find_all ('a', href=True, class_='b_attribution')]
        return results[:num_results]

    def duckduckgo_search(self, query, num_results=10):
        headers = {"User-Agent": "Mozilla/5.0"}
        search_url = f"https://duckduckgo.com/html/?q={query}"
        response = requests.get (search_url, headers=headers)
        soup = BeautifulSoup (response.text, "html.parser")
        results = [link.get ('href') for link in soup.find_all ('a', href=True, class_='result__url')]
        return results[:num_results]

    def onion_search(self, query, num_results=10):
        headers = {"User-Agent": "Mozilla/5.0"}
        search_url = f"https://duckduckgo.com/html/?q={query} site:.onion"
        response = requests.get (search_url, headers=headers)
        soup = BeautifulSoup (response.text, "html.parser")
        results = [link.get ('href') for link in soup.find_all ('a', href=True, class_='result__url')]
        return [url for url in results if ".onion" in url][:num_results]

        # Onion search
        for result in self.onion_search (keyword, 500):
            self.make_links_clickable (result)
            self.results.append (result)
            self.root.update_idletasks ( )

    def perform_facebook_search(self, keyword, sector, location, gender, company):
        facebook_results = []

        # Configuration du navigateur Selenium
        chrome_service = ChromeService ("chromedriver.exe")
        chrome_service.start ( )
        options = webdriver.ChromeOptions ( )
        options.add_argument ("--headless")  # Exécution en mode headless (sans interface graphique)
        driver = webdriver.Chrome (service=chrome_service, options=options)

        try:
            # Ouvrir la page de recherche Facebook
            driver.get ("https://www.facebook.com")

            # Remplir les champs de recherche
            search_box = driver.find_element (By.NAME, "q")
            search_box.send_keys (keyword + f" {sector} {location} {gender} {company}")
            search_box.send_keys (Keys.RETURN)

            # Attendez que la page de résultats se charge (ajuster le délai si nécessaire)
            driver.implicitly_wait (10)

            # Extraire les résultats de la page (ajuster le sélecteur CSS selon la structure de la page)
            result_elements = driver.find_elements (By.CSS_SELECTOR, ".your-result-css-selector")

            for element in result_elements:
                result_url = element.get_attribute ("href")
                facebook_results.append (result_url)

        except Exception as e:
            print ("Erreur lors de la recherche Facebook:", e)

        finally:
            # Fermez le navigateur Selenium
            driver.quit ( )
            chrome_service.stop ( )

        return facebook_results

    def perform_linkedin_search(self, keyword, sector, location, gender, company):
        linkedin_results = []

        # Configuration du navigateur Selenium (utilisez le chemin vers votre propre webdriver)
        chrome_service = ChromeService ("chromedriver.exe")
        chrome_service.start ( )
        options = webdriver.ChromeOptions ( )
        options.add_argument ("--headless")
        driver = webdriver.Chrome (service=chrome_service, options=options)

        try:
            # Ouvrir la page de recherche LinkedIn
            driver.get ("https://www.linkedin.com")

            # Remplir les champs de recherche
            search_box = driver.find_element (By.NAME, "keywords")
            search_box.send_keys (keyword + f" {sector} {location} {gender} {company}")
            search_box.send_keys (Keys.RETURN)

            # Attendez que la page de résultats se charge (ajuster le délai si nécessaire)
            driver.implicitly_wait (10)

            # Extraire les résultats de la page (ajuster le sélecteur CSS selon la structure de la page)
            result_elements = driver.find_elements (By.CSS_SELECTOR, ".your-result-css-selector")

            for element in result_elements:
                result_url = element.get_attribute ("href")
                linkedin_results.append (result_url)

        except Exception as e:
            print ("Erreur lors de la recherche LinkedIn:", e)

        finally:
            # Fermez le navigateur Selenium
            driver.quit ( )
            chrome_service.stop ( )

        return linkedin_results

    def search_invisible_links(self, url):
        invisible_links = []

        # Vérifiez d'abord si l'URL est une chaîne de caractères
        if not isinstance(url, str):
            return invisible_links
       
        try:
            # Ajoutez une validation de schéma avant de rechercher des liens invisibles
            if not url.startswith('http://') and not url.startswith('https://'):
                url = 'https://' + url

            # Effectuez une requête HTTP pour obtenir le contenu de la page
            response = requests.get(url)

            # Vérifiez si la requête a réussi
            if response.status_code == 200:
                # Utilisez BeautifulSoup pour analyser le contenu HTML
                soup = BeautifulSoup (response.text, 'html.parser')

                # Recherchez les liens invisibles dans le code HTML de la page
                for link in soup.find_all('a'):
                    href = link.get('href')
                    style = link.get('style')
                    if href and (not style or 'display: none' not in style):
                        invisible_links.append(href)

        except Exception as e:
            print (f"Erreur lors de la recherche de liens invisibles : {e}")

        return invisible_links

    def on_logo_enter(self, event):
        self.logo_label.config(cursor="hand2")

    def on_logo_leave(self, event):
        self.logo_label.config(cursor="arrow")

    def open_avhiral_website(self, event):
        webbrowser.open("https://www.avhiral.com")

    def open_clicked_link(self, event):
        tag = self.results_text.tag_names(tk.CURRENT)[0]
        clicked_range = self.results_text.tag_prevrange(tag, self.results_text.index(tk.CURRENT))
        url = self.results_text.get(clicked_range[0], clicked_range[1])
        webbrowser.open(url.strip())

    def change_cursor_to_hand(self, event, hover_tag):
        self.results_text.tag_add(hover_tag, self.results_text.index(tk.CURRENT),
                                  self.results_text.index(tk.CURRENT) + "+1c")
        self.results_text.config(cursor="hand2")

    def change_cursor_to_arrow(self, event, hover_tag=None):
        if hover_tag:
            self.results_text.tag_remove(hover_tag, "1.0", tk.END)
        self.results_text.config(cursor="arrow")

    def navigate_results(self, direction):
        if self.results:
            if direction == "next":
                self.current_index = (self.current_index + 1) % len(self.results)
            elif direction == "prev":
                self.current_index = (self.current_index - 1) % len(self.results)
            self.display_current_result()

    def display_results(self):
        self.results_text.delete(1.0, tk.END)
        for result in self.results:
            self.make_links_clickable(result)

    def make_links_clickable(self, text):
        tag = "url_" + str(self.results_text.index(tk.END))
        self.results_text.insert(tk.END, text + "\n", tag)
        self.results_text.tag_bind(tag, "<Button-1>", self.open_clicked_link)
        self.results_text.tag_bind(tag, "<Enter>", lambda event, t=tag: self.change_cursor_to_hand(event, t))
        self.results_text.tag_bind(tag, "<Leave>", lambda event, t=tag: self.change_cursor_to_arrow(event, t))

    def open_clicked_link(self, event):
        tag = self.results_text.tag_names(tk.CURRENT)[0]
        clicked_range = self.results_text.tag_prevrange(tag, self.results_text.index(tk.CURRENT))
        if clicked_range:
            url = self.results_text.get(clicked_range[0], clicked_range[1])
            webbrowser.open(url.strip())

    def change_cursor_to_hand(self, event, hover_tag):
        self.results_text.tag_add("url_hover", self.results_text.index(hover_tag + ".first"),
                                  self.results_text.index(hover_tag + ".last"))
        self.results_text.config(cursor="hand2")

    def change_cursor_to_arrow(self, event, hover_tag=None):
        if hover_tag:
            self.results_text.tag_remove("url_hover", "1.0", tk.END)
        self.results_text.config(cursor="arrow")

    def show_url_on_hover(self, url):
        self.url_label.config(text=url)

    def open_clicked_link(self, event):
        tag = self.results_text.tag_names(tk.CURRENT)[0]
        clicked_range = self.results_text.tag_prevrange(tag, self.results_text.index(tk.CURRENT))
        if clicked_range:
            url = self.results_text.get(clicked_range[0], clicked_range[1])
            # Si l'URL est un lien .onion, utilisez le navigateur Tor, sinon utilisez le navigateur par défaut.
            if ".onion" in url:
                tor_browser_path = r'C:\Users\David\Desktop\Tor Browser\Browser\firefox.exe'  # Spécifiez le chemin vers votre navigateur Tor ici.
                webbrowser.register('tor', None, webbrowser.BackgroundBrowser(tor_browser_path))
                webbrowser.get('tor').open(url.strip())
            else:
                webbrowser.open(url.strip())

    def display_current_result(self):
        self.results_text.delete(1.0, tk.END)
        if self.results:
            self.make_links_clickable(self.results[self.current_index])


if __name__ == "__main__":
    root = tk.Tk()
    root.state('zoomed')
    app = AdvancedSearchApp(root)

    # Ajouter une étiquette pour afficher l'URL lors du survol
    app.url_label = tk.Label(root, text="", foreground="blue")
    app.url_label.pack(pady=(0, 10), padx=10, anchor='w')

    root.mainloop()
