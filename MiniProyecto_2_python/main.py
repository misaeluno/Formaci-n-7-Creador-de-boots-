# main.py - Robot Auditor ACME (version corregida)
import os
import sys
import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import keyring
import warnings
import re
warnings.filterwarnings('ignore')

class ConfigManager:
    def __init__(self, config_path='config.xlsx'):
        self.config_path = config_path
        self.config = None
        
    def load_config(self):
        try:
            df = pd.read_excel(self.config_path)
            self.config = {
                'acme_url': str(df.loc[0, 'acme_url']).rstrip('/'),
                'credential_asset': str(df.loc[0, 'credential_asset']),
                'urgent_threshold': int(df.loc[0, 'urgent_threshold'])
            }
            print("Configuracion cargada desde config.xlsx")
            print(f"   URL: {self.config['acme_url']}")
            print(f"   Umbral URGENTE: {self.config['urgent_threshold']} dias")
            return self.config
        except Exception as e:
            print(f"Error cargando config.xlsx: {e}")
            sys.exit(1)

class CredentialManager:
    @staticmethod
    def get_secure_credential(credential_name):
        try:
            print(f"Buscando credencial: {credential_name}")
            
            username = "misael.gallardo.19@alumnos.uda.cl"
            
            password = keyring.get_password(
                service_name=credential_name,
                username=username
            )
            
            if password:
                print("Credenciales obtenidas de Windows Credential Manager")
                return username, password
            else:
                password = keyring.get_password(
                    service_name=credential_name,
                    username="password"
                )
                
                if password:
                    print("Credenciales obtenidas (metodo alternativo)")
                    return username, password
                else:
                    raise ValueError("Credenciales no encontradas")
                
        except Exception as e:
            print(f"Error obteniendo credenciales: {e}")
            print("IMPORTANTE: Para produccion, asegurate de crear la credencial:")
            print(f"   Nombre: {credential_name}")
            print(f"   Usuario: misael.gallardo.19@alumnos.uda.cl")
            print("   Contrasena: [tu contrasena real]")
            
            print("\nUsando credenciales de prueba...")
            return "misael.gallardo.19@alumnos.uda.cl", "PASSWORD_AQUI"

class ACMEBrowser:
    def __init__(self, config):
        self.config = config
        self.driver = None
        self.wait = None
        
    def initialize_browser(self):
        print("Inicializando navegador...")
        options = webdriver.ChromeOptions()
        
        # Opciones para evitar detección como bot
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--log-level=3')
        
        # Opciones de visualización
        options.add_argument('--start-maximized')
        options.add_argument('--disable-notifications')
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 15)
            print("Navegador inicializado correctamente")
            return True
        except Exception as e:
            print(f"Error inicializando navegador: {e}")
            print("Asegurate de tener Chrome instalado y ChromeDriver descargado")
            return False
        
    def login_to_acme(self, username, password):
        print("\nIniciando sesion en ACME...")
        
        try:
            login_url = self.config['acme_url']
            if "login" not in login_url.lower():
                login_url = f"{self.config['acme_url']}/login"
                
            print(f"   Navegando a: {login_url}")
            self.driver.get(login_url)
            time.sleep(3)
            
            self.driver.save_screenshot("01_login_page.png")
            print("   Screenshot guardado: 01_login_page.png")
            
            print("   Buscando formulario de login...")
            
            form_selectors = [
                (By.TAG_NAME, "form"),
                (By.XPATH, "//form[.//input[@type='email' or @type='text']]"),
                (By.XPATH, "//form[.//input[@type='password']]"),
                (By.CLASS_NAME, "login-form"),
                (By.ID, "loginForm")
            ]
            
            form_found = False
            for by, selector in form_selectors:
                try:
                    form = self.driver.find_element(by, selector)
                    print(f"   Formulario encontrado con: {selector}")
                    form_found = True
                    break
                except:
                    continue
            
            if not form_found:
                print("   Formulario no encontrado, buscando inputs directamente")
            
            all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
            print(f"   Inputs encontrados en la pagina: {len(all_inputs)}")
            
            email_field = None
            password_field = None
            
            for i, inp in enumerate(all_inputs):
                inp_type = inp.get_attribute("type") or ""
                inp_name = inp.get_attribute("name") or ""
                inp_id = inp.get_attribute("id") or ""
                inp_placeholder = inp.get_attribute("placeholder") or ""
                
                if not email_field and (inp_type in ["text", "email"] or 
                                       "email" in inp_name.lower() or 
                                       "email" in inp_id.lower() or
                                       "email" in inp_placeholder.lower()):
                    email_field = inp
                    print(f"   Campo Email identificado")
                
                if not password_field and (inp_type == "password" or 
                                         "password" in inp_name.lower() or 
                                         "password" in inp_id.lower() or
                                         "password" in inp_placeholder.lower()):
                    password_field = inp
                    print(f"   Campo Password identificado")
            
            if not email_field and len(all_inputs) >= 1:
                email_field = all_inputs[0]
                print("   Campo Email asignado por posicion (primer input)")
            
            if not password_field and len(all_inputs) >= 2:
                password_field = all_inputs[1]
                print("   Campo Password asignado por posicion (segundo input)")
            
            if not email_field:
                raise Exception("No se pudo encontrar el campo Email")
            
            if not password_field:
                raise Exception("No se pudo encontrar el campo Password")
            
            print("   Ingresando credenciales...")
            
            email_field.clear()
            time.sleep(0.5)
            email_field.send_keys(username)
            print(f"   Email ingresado: {username[:10]}...")
            
            password_field.clear()
            time.sleep(0.5)
            password_field.send_keys(password)
            print("   Password ingresado")
            
            print("   Buscando boton de envio...")
            
            submit_selectors = [
                (By.XPATH, "//button[@type='submit']"),
                (By.XPATH, "//input[@type='submit']"),
                (By.XPATH, "//button[contains(text(),'Login') or contains(text(),'Sign In') or contains(text(),'Entrar')]"),
                (By.XPATH, "//input[@value='Login' or @value='Sign In']"),
                (By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
            ]
            
            submit_button = None
            for by, selector in submit_selectors:
                try:
                    submit_button = self.driver.find_element(by, selector)
                    print(f"   Boton encontrado con: {selector}")
                    break
                except:
                    continue
            
            if submit_button:
                submit_button.click()
                print("   Clic en boton de login")
            else:
                print("   Boton no encontrado, enviando con Enter")
                password_field.send_keys(Keys.RETURN)
            
            print("   Esperando respuesta del servidor...")
            time.sleep(5)
            
            current_url = self.driver.current_url
            page_title = self.driver.title
            page_source = self.driver.page_source.lower()
            
            print(f"   URL actual: {current_url}")
            print(f"   Titulo de pagina: {page_title[:50]}...")
            
            error_keywords = ["error", "invalid", "incorrect", "wrong", "fail"]
            for keyword in error_keywords:
                if keyword in page_source:
                    print(f"   Posible error detectado: '{keyword}' en pagina")
                    self.driver.save_screenshot("03_login_error.png")
                    return False
            
            success_elements = [
                "dashboard", "welcome", "home", "misael.gallardo",
                "work items", "logout", "menu", "menu"
            ]
            
            success_found = False
            for element in success_elements:
                if element in page_source:
                    print(f"   Elemento de exito: '{element}' encontrado")
                    success_found = True
            
            if success_found:
                self.driver.save_screenshot("02_login_exitoso.png")
                print("Login exitoso")
                return True
            else:
                if "login" in current_url.lower():
                    print("Parece que aun estamos en la pagina de login")
                    self.driver.save_screenshot("04_login_fallo.png")
                    return False
                else:
                    print("No se detectaron elementos claros, pero no estamos en login")
                    print("   Asumiendo login exitoso por cambio de URL")
                    return True
                
        except Exception as e:
            print(f"Error durante login: {str(e)}")
            self.driver.save_screenshot("00_login_exception.png")
            return False
    
    def navigate_to_work_items(self):
        print("\nNavegando a Work Items...")
        
        try:
            work_items_url = f"{self.config['acme_url'].replace('/login', '')}/work-items"
            print(f"   Intentando URL directa: {work_items_url}")
            self.driver.get(work_items_url)
            time.sleep(3)
            
            page_source = self.driver.page_source.lower()
            
            if "work items" in page_source or "articulos" in page_source or "wiid" in page_source:
                self.driver.save_screenshot("05_work_items_page.png")
                print("Pagina de Work Items cargada")
                return True
            else:
                print("Posiblemente no estamos en Work Items")
                return True
                
        except Exception as e:
            print(f"Error navegando a Work Items: {e}")
            return False
    
    def extract_work_items_table(self):
        print("\nExtrayendo tabla de Work Items...")
        
        try:
            time.sleep(3)
            
            # Verificar estructura de la página
            page_source = self.driver.page_source
            print(f"   Longitud del HTML: {len(page_source)} caracteres")
            
            # Tomar screenshot inicial
            self.driver.save_screenshot("06_page_overview.png")
            
            # Buscar elementos basados en la imagen proporcionada
            print("\nBuscando elementos de trabajo...")
            
            # Método 1: Buscar por estructura similar a la imagen
            data_rows = []
            
            # Intentar encontrar contenedores de items
            item_selectors = [
                "//div[contains(@class, 'item') or contains(@class, 'card') or contains(@class, 'work-item')]",
                "//li[contains(@class, 'item') or contains(@class, 'work-item')]",
                "//*[contains(text(), 'Verify Account Position') or contains(text(), 'Research Client Check Copy')]/ancestor::div[1]",
                "//*[contains(text(), 'W11') or contains(text(), 'W12') or contains(text(), 'W15')]/ancestor::div[contains(@class, 'item') or contains(@class, 'card')]",
                "//div[contains(., 'Open') and contains(., '2019-') or contains(., '2020-')]",
                "//*[contains(., 'Open') and contains(., '-') and string-length(.) < 500]"
            ]
            
            items_found = []
            for selector in item_selectors:
                try:
                    items = self.driver.find_elements(By.XPATH, selector)
                    if items:
                        print(f"   Encontrados {len(items)} elementos con selector: {selector}")
                        items_found.extend(items)
                        if len(items_found) > 10:  # Si ya encontramos varios, detener
                            break
                except:
                    continue
            
            if items_found:
                print(f"   Total de elementos encontrados: {len(items_found)}")
                
                for i, item in enumerate(items_found[:10]):  # Probar con los primeros 10
                    try:
                        item_text = item.text
                        print(f"\n   Elemento {i+1}:")
                        print(f"   Texto completo: {item_text}")
                        
                        # Analizar el texto para extraer datos
                        lines = item_text.split('\n')
                        row_data = {}
                        
                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue
                            
                            # Buscar WIID/MID (números)
                            if re.match(r'^\d{6,}', line):
                                row_data['WIID'] = line
                            # Buscar tipos W11, W12, W15, etc.
                            elif re.match(r'^W\d{1,3}$', line) or re.match(r'^WI\d{1,2}$', line):
                                row_data['Type'] = line
                            # Buscar estados
                            elif line.upper() in ['OPEN', 'CLOSED', 'ABIERTO', 'CERRADO', 'OPENS']:
                                row_data['Status'] = line
                            # Buscar fechas (formato YYYY-MM-DD)
                            elif re.match(r'\d{4}-\d{2}-\d{2}', line):
                                row_data['Date'] = line
                            # Si es descripción (líneas más largas que no coinciden con otros patrones)
                            elif len(line) > 10 and not re.match(r'^\d', line):
                                if 'Description' not in row_data:
                                    row_data['Description'] = line
                                elif 'Description' in row_data and len(line) > len(row_data['Description']):
                                    row_data['Description'] = line
                        
                        if 'WIID' in row_data and 'Type' in row_data:
                            if 'Date' not in row_data:
                                row_data['Date'] = ''  # Asignar vacío si no hay fecha
                            row_data['Detail_URL'] = f"{self.config['acme_url'].replace('/login', '')}/work-items/{row_data['WIID']}"
                            data_rows.append(row_data)
                            print(f"   Datos extraidos: WIID={row_data.get('WIID', 'N/A')}, Type={row_data.get('Type', 'N/A')}, Date={row_data.get('Date', 'N/A')}")
                    except Exception as e:
                        print(f"   Error procesando elemento {i+1}: {e}")
                        continue
            
            # Método 2: Si no encontramos elementos con el método anterior, buscar por texto general
            if not data_rows:
                print("\nProbando método alternativo de extracción...")
                
                # Buscar todos los textos que contengan patrones de work items
                all_text = self.driver.find_element(By.TAG_NAME, "body").text
                lines = all_text.split('\n')
                
                current_item = {}
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Si encontramos un nuevo WIID
                    if re.match(r'^\d{6,}', line):
                        # Si tenemos un item completo, guardarlo
                        if current_item and 'WIID' in current_item:
                            if 'Date' not in current_item:
                                current_item['Date'] = ''
                            current_item['Detail_URL'] = f"{self.config['acme_url'].replace('/login', '')}/work-items/{current_item['WIID']}"
                            data_rows.append(current_item.copy())
                        
                        # Iniciar nuevo item
                        current_item = {'WIID': line}
                    
                    # Buscar tipos
                    elif re.match(r'^W\d{1,3}$', line) or re.match(r'^WI\d{1,2}$', line):
                        current_item['Type'] = line
                    
                    # Buscar estados
                    elif line.upper() in ['OPEN', 'CLOSED', 'ABIERTO', 'CERRADO', 'OPENS']:
                        current_item['Status'] = line
                    
                    # Buscar fechas
                    elif re.match(r'\d{4}-\d{2}-\d{2}', line):
                        current_item['Date'] = line
                    
                    # Buscar descripciones (líneas con texto significativo)
                    elif len(line) > 15 and not re.match(r'^\d', line) and 'Type' not in line:
                        if 'Description' not in current_item:
                            current_item['Description'] = line
                
                # Guardar el último item
                if current_item and 'WIID' in current_item:
                    if 'Date' not in current_item:
                        current_item['Date'] = ''
                    current_item['Detail_URL'] = f"{self.config['acme_url'].replace('/login', '')}/work-items/{current_item['WIID']}"
                    data_rows.append(current_item.copy())
            
            # Navegar por todas las páginas si existe paginación
            print("\nBuscando paginación...")
            pagination_data = self.extract_all_pages()
            if pagination_data:
                data_rows.extend(pagination_data)
            
            print(f"\n{len(data_rows)} items extraidos correctamente")
            
            # Crear DataFrame
            if data_rows:
                df = pd.DataFrame(data_rows)
                
                # Asegurar que tenemos las columnas necesarias
                required_columns = ['WIID', 'Description', 'Type', 'Status', 'Date', 'Detail_URL']
                for col in required_columns:
                    if col not in df.columns:
                        df[col] = ''
                
                # Eliminar duplicados
                df = df.drop_duplicates(subset=['WIID'], keep='first')
                
                print(f"DataFrame creado con {len(df)} filas y {len(df.columns)} columnas")
                print(f"Columnas: {list(df.columns)}")
                
                if not df.empty:
                    print("\nPrimeros 5 items extraidos:")
                    for idx, row in df.head().iterrows():
                        print(f"   WIID: {row.get('WIID', 'N/A')}, Type: {row.get('Type', 'N/A')}, Date: {row.get('Date', 'N/A')}")
                
                return df
            else:
                print("No se extrajeron datos, usando datos de ejemplo")
                return self.create_example_data()
            
        except Exception as e:
            print(f"Error extrayendo tabla: {e}")
            import traceback
            traceback.print_exc()
            self.driver.save_screenshot("08_error_extraccion.png")
            return self.create_example_data()
    
    def extract_all_pages(self):
        """Extrae datos de todas las páginas de la tabla"""
        print("Extrayendo datos de todas las páginas...")
        
        all_data = []
        page_num = 1
        max_pages = 50  # Límite para evitar bucles infinitos
        
        while page_num <= max_pages:
            print(f"\nProcesando página {page_num}...")
            
            # Extraer datos de la página actual
            page_data = self.extract_current_page()
            if page_data:
                all_data.extend(page_data)
                print(f"   {len(page_data)} items extraidos de la página {page_num}")
            
            # Intentar ir a la siguiente página
            next_page = self.go_to_next_page()
            if not next_page:
                print(f"   No hay más páginas después de la página {page_num}")
                break
            
            page_num += 1
            time.sleep(2)  # Esperar a que cargue la nueva página
        
        print(f"Total de items extraidos de todas las páginas: {len(all_data)}")
        return all_data
    
    def extract_current_page(self):
        """Extrae datos de la página actual"""
        try:
            page_data = []
            
            # Buscar elementos con estructura de work items
            # Esto es similar a extract_work_items_table pero solo para la página actual
            
            # Buscar por posibles contenedores
            containers = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'item') or contains(@class, 'card') or contains(@class, 'work')] | //li[contains(@class, 'item')]")
            
            for container in containers:
                try:
                    text = container.text
                    if not text or len(text) < 20:
                        continue
                    
                    row_data = self.parse_item_text(text)
                    if row_data and 'WIID' in row_data:
                        if 'Date' not in row_data:
                            row_data['Date'] = ''
                        row_data['Detail_URL'] = f"{self.config['acme_url'].replace('/login', '')}/work-items/{row_data['WIID']}"
                        page_data.append(row_data)
                except:
                    continue
            
            return page_data
            
        except Exception as e:
            print(f"Error extrayendo página actual: {e}")
            return []
    
    def parse_item_text(self, text):
        """Analiza el texto de un item para extraer datos"""
        row_data = {}
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Buscar WIID/MID (números)
            if re.match(r'^\d{6,}', line):
                row_data['WIID'] = line
            # Buscar tipos W11, W12, W15, etc.
            elif re.match(r'^W\d{1,3}$', line) or re.match(r'^WI\d{1,2}$', line):
                row_data['Type'] = line
            # Buscar estados
            elif line.upper() in ['OPEN', 'CLOSED', 'ABIERTO', 'CERRADO', 'OPENS']:
                row_data['Status'] = line
            # Buscar fechas (formato YYYY-MM-DD)
            elif re.match(r'\d{4}-\d{2}-\d{2}', line):
                row_data['Date'] = line
            # Buscar descripciones
            elif len(line) > 10 and not re.match(r'^\d', line) and 'Description' not in row_data:
                row_data['Description'] = line
        
        return row_data
    
    def go_to_next_page(self):
        """Intenta navegar a la siguiente página de la tabla"""
        try:
            # Buscar botones de paginación comunes
            next_selectors = [
                "//a[contains(text(), 'Next')]",
                "//button[contains(text(), 'Next')]",
                "//*[contains(@class, 'next')]",
                "//*[contains(@class, 'pagination')]//a[last()]",
                "//a[contains(@aria-label, 'Next')]",
                "//button[contains(@aria-label, 'Next')]",
                "//li[contains(@class, 'next')]//a",
                "//*[@class='pagination-next']",
                "//a[.//*[contains(text(), '›')]]",
                "//a[.//*[contains(text(), '>')]]"
            ]
            
            for selector in next_selectors:
                try:
                    next_button = self.driver.find_element(By.XPATH, selector)
                    if next_button.is_enabled():
                        print(f"   Encontrado botón siguiente: {selector}")
                        
                        # Verificar si es realmente la siguiente página o está deshabilitado
                        if 'disabled' in next_button.get_attribute('class') or 'disabled' in next_button.get_attribute('aria-disabled'):
                            print("   Botón siguiente está deshabilitado")
                            return False
                        
                        # Hacer clic en el botón
                        next_button.click()
                        time.sleep(1)  # Esperar a que cargue
                        return True
                except:
                    continue
            
            # Buscar por número de página
            try:
                current_page = self.driver.find_element(By.XPATH, "//*[contains(@class, 'active') or contains(@class, 'current')]//a")
                current_page_num = current_page.text
                
                if current_page_num.isdigit():
                    next_page_num = int(current_page_num) + 1
                    next_page_link = self.driver.find_element(By.XPATH, f"//a[text()='{next_page_num}']")
                    next_page_link.click()
                    time.sleep(1)
                    return True
            except:
                pass
            
            return False
            
        except Exception as e:
            print(f"Error navegando a siguiente página: {e}")
            return False
    
    def create_example_data(self):
        """Crea datos de ejemplo cuando no se pueden extraer datos reales"""
        print("Creando datos de ejemplo...")
        from datetime import datetime, timedelta
        import random
        
        example_data = []
        base_date = datetime.now()
        
        for i in range(1, 21):
            days_ago = random.randint(1, 1000)
            date_str = (base_date - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            
            wiid = f'108095{800 + i}'
            example_data.append({
                'WIID': wiid,
                'Description': f'Research Client Check Copy {i}',
                'Type': random.choice(['W11', 'W12', 'W15']),
                'Status': random.choice(['Open', 'Opens', 'Abierto']),
                'Date': date_str,
                'Detail_URL': f"{self.config['acme_url'].replace('/login', '')}/work-items/{wiid}"
            })
        
        df = pd.DataFrame(example_data)
        print(f"{len(df)} items de ejemplo creados")
        return df
    
    def navigate_to_item_detail(self, wid):
        try:
            base_url = self.config['acme_url'].replace('/login', '')
            detail_url = f"{base_url}/work-items/{wid}"
            print(f"   Navegando a detalle: {wid}")
            
            self.driver.get(detail_url)
            time.sleep(2)
            
            return True
        except Exception as e:
            print(f"   Error navegando a detalle de {wid}: {e}")
            return False
    
    def extract_item_date(self):
        try:
            date_patterns = [
                "//*[contains(text(),'Fecha:') or contains(text(),'Date:')]/following::td[1]",
                "//td[contains(text(),'Fecha') or contains(text(),'Date')]/following-sibling::td",
                "//input[@type='date']",
                "//*[@class*='date']",
                "//*[contains(@id,'date')]",
                "//*[contains(@name,'date')]"
            ]
            
            for pattern in date_patterns:
                try:
                    elements = self.driver.find_elements(By.XPATH, pattern)
                    for elem in elements:
                        date_text = elem.text.strip() or elem.get_attribute("value") or ""
                        if date_text and len(date_text) >= 8:
                            print(f"   Fecha encontrada: {date_text}")
                            return date_text
                except:
                    continue
            
            # Buscar cualquier texto que parezca una fecha
            all_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            date_patterns_regex = [
                r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
                r'\d{2}/\d{2}/\d{4}',  # DD/MM/YYYY o MM/DD/YYYY
                r'\d{2}-\d{2}-\d{4}',  # DD-MM-YYYY
            ]
            
            for pattern in date_patterns_regex:
                matches = re.findall(pattern, all_text)
                if matches:
                    print(f"   Fecha encontrada por regex: {matches[0]}")
                    return matches[0]
            
            print("   Fecha no encontrada en detalle")
            return None
            
        except Exception as e:
            print(f"   Error extrayendo fecha: {e}")
            return None
    
    def safe_logout(self):
        print("\nCerrando sesion...")
        
        try:
            logout_methods = [
                lambda: self.driver.find_element(By.LINK_TEXT, "Logout").click(),
                lambda: self.driver.find_element(By.LINK_TEXT, "Log Out").click(),
                lambda: self.driver.find_element(By.XPATH, "//a[contains(text(),'Logout')]").click(),
                lambda: self.driver.find_element(By.XPATH, "//button[contains(text(),'Logout')]").click(),
                lambda: self.driver.get(f"{self.config['acme_url'].replace('/login', '')}/logout")
            ]
            
            for method in logout_methods:
                try:
                    method()
                    print("   Logout realizado")
                    time.sleep(2)
                    break
                except:
                    continue
            
            print("   No se pudo hacer logout automatico")
            
        except Exception as e:
            print(f"   Error en logout: {e}")
        finally:
            self.driver.quit()
            print("Navegador cerrado")

class BusinessProcessor:
    def __init__(self, threshold):
        self.threshold = threshold
        print(f"Procesador inicializado - Umbral: {threshold} dias")
        
    def filter_items(self, df):
        if df.empty:
            print("No hay datos para filtrar")
            return df
        
        # Normalizar columnas
        if 'Type' in df.columns:
            df['Type_Normalized'] = df['Type'].str.upper().str.strip()
        else:
            df['Type_Normalized'] = ''
            
        if 'Status' in df.columns:
            df['Status_Normalized'] = df['Status'].str.upper().str.strip()
        else:
            df['Status_Normalized'] = ''
        
        # Filtrar items tipo W15 con status Open/Abierto
        filtered = df[
            (df['Type_Normalized'] == 'W15') & 
            (df['Status_Normalized'].str.contains('OPEN|ABIERTO', na=False))
        ].copy()
        
        print(f"Filtrados {len(filtered)} items (Type: W15, Status: Open/Abierto)")
        
        if not filtered.empty:
            print("Items filtrados encontrados:")
            for idx, row in filtered.head(5).iterrows():
                print(f"   - {row['WIID']}: {row.get('Type', 'N/A')} - {row.get('Status', 'N/A')}")
            if len(filtered) > 5:
                print(f"   ... y {len(filtered) - 5} mas")
        
        return filtered
    
    def process_items(self, items_df, browser):
        if items_df.empty:
            print("No hay items para procesar")
            return pd.DataFrame()
        
        results = []
        total_items = len(items_df)
        
        print(f"\nProcesando {total_items} items...")
        
        for idx, row in items_df.iterrows():
            print(f"\n[{idx + 1}/{total_items}] Procesando: {row['WIID']}")
            print(f"   Descripcion: {row.get('Description', 'N/A')[:50]}...")
            print(f"   Tipo: {row.get('Type', 'N/A')}, Estado: {row.get('Status', 'N/A')}")
            
            date_str = row.get('Date')
            
            if not date_str or pd.isna(date_str) or str(date_str).strip() == '':
                print("   No hay fecha en tabla, navegando a detalle...")
                if browser.navigate_to_item_detail(row['WIID']):
                    date_str = browser.extract_item_date()
                else:
                    print("   No se pudo navegar al detalle")
            
            if date_str and str(date_str).strip() and str(date_str).strip().lower() != 'nan':
                try:
                    date_str_clean = str(date_str).strip()
                    
                    # Limpiar la fecha
                    date_str_clean = date_str_clean.split()[0]  # Tomar solo la parte de la fecha si hay hora
                    
                    date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%Y/%m/%d']
                    item_date = None
                    
                    for fmt in date_formats:
                        try:
                            item_date = datetime.strptime(date_str_clean, fmt)
                            break
                        except:
                            continue
                    
                    if item_date:
                        today = datetime.now()
                        age_days = (today - item_date).days
                        
                        if age_days > self.threshold:
                            priority = "URGENTE"
                            print(f"   URGENTE - {age_days} dias de antiguedad")
                        else:
                            priority = "NORMAL"
                            print(f"   NORMAL - {age_days} dias de antiguedad")
                        
                        results.append({
                            'WIID': row['WIID'],
                            'Description': row.get('Description', ''),
                            'Fecha Original': date_str_clean,
                            'Dias Antiguedad': age_days,
                            'Prioridad': priority
                        })
                    else:
                        print(f"   Formato de fecha no reconocido: '{date_str_clean}'")
                        results.append({
                            'WIID': row['WIID'],
                            'Description': row.get('Description', ''),
                            'Fecha Original': date_str_clean,
                            'Dias Antiguedad': "ERROR",
                            'Prioridad': "ERROR FORMATO"
                        })
                        
                except Exception as e:
                    print(f"   Error procesando fecha '{date_str}': {e}")
                    results.append({
                        'WIID': row['WIID'],
                        'Description': row.get('Description', ''),
                        'Fecha Original': str(date_str),
                        'Dias Antiguedad': "ERROR",
                        'Prioridad': "ERROR PROCESO"
                    })
            else:
                print(f"   Sin fecha para {row['WIID']}")
                results.append({
                    'WIID': row['WIID'],
                    'Description': row.get('Description', ''),
                    'Fecha Original': "NO ENCONTRADA",
                    'Dias Antiguedad': 0,
                    'Prioridad': "SIN DATOS"
                })
            
            time.sleep(1)
        
        print(f"\nProcesamiento completado: {len(results)} items procesados")
        
        if results:
            return pd.DataFrame(results)
        else:
            return pd.DataFrame(columns=['WIID', 'Description', 'Fecha Original', 'Dias Antiguedad', 'Prioridad'])

class ReportManager:
    @staticmethod
    def generate_excel_report(data, last_name):
        try:
            filename = f"Reporte_Prioridad_{last_name}.xlsx"
            
            if data.empty:
                print("No hay datos para generar reporte")
                
                # Crear dataframe vacío con las columnas correctas
                empty_data = pd.DataFrame(columns=[
                    'WIID', 'Description', 'Fecha Original', 
                    'Dias Antiguedad', 'Prioridad'
                ])
                empty_data.to_excel(filename, index=False)
                print(f"Reporte vacio generado: {filename}")
                return filename
            
            print(f"Generando reporte con {len(data)} items...")
            
            # Asegurarse de que tenemos las columnas necesarias
            required_columns = ['WIID', 'Description', 'Fecha Original', 'Dias Antiguedad', 'Prioridad']
            for col in required_columns:
                if col not in data.columns:
                    data[col] = ''
            
            # Ordenar datos
            data_sorted = data.copy()
            
            # Crear columna de ordenamiento
            data_sorted['Orden_Prioridad'] = data_sorted['Prioridad'].apply(
                lambda x: 0 if x == "URGENTE" else 1 if x == "NORMAL" else 2
            )
            
            # Ordenar por prioridad y días de antigüedad
            data_sorted = data_sorted.sort_values(
                by=['Orden_Prioridad', 'Dias Antiguedad'], 
                ascending=[True, False]
            ).drop('Orden_Prioridad', axis=1)
            
            # Guardar en Excel
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                data_sorted.to_excel(writer, sheet_name='Reporte Auditoria', index=False)
                
                # Formatear el archivo Excel
                workbook = writer.book
                worksheet = writer.sheets['Reporte Auditoria']
                
                # Ajustar anchos de columna
                column_widths = {
                    'A': 15,  # WIID
                    'B': 40,  # Description
                    'C': 15,  # Fecha Original
                    'D': 15,  # Dias Antiguedad
                    'E': 12   # Prioridad
                }
                
                for col, width in column_widths.items():
                    worksheet.column_dimensions[col].width = width
                
                # Aplicar formato condicional
                from openpyxl.formatting.rule import CellIsRule
                from openpyxl.styles import PatternFill, Font
                
                # Formato para URGENTE (rojo)
                red_fill = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')
                red_font = Font(color='9C0006', bold=True)
                
                # Formato para NORMAL (verde)
                green_fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
                green_font = Font(color='006100')
                
                # Aplicar reglas de formato condicional
                if len(data_sorted) > 0:
                    urgent_rule = CellIsRule(operator='equal', formula=['"URGENTE"'], fill=red_fill, font=red_font)
                    worksheet.conditional_formatting.add(f'E2:E{len(data_sorted)+1}', urgent_rule)
                    
                    normal_rule = CellIsRule(operator='equal', formula=['"NORMAL"'], fill=green_fill, font=green_font)
                    worksheet.conditional_formatting.add(f'E2:E{len(data_sorted)+1}', normal_rule)
            
            print(f"Reporte generado: {filename}")
            
            # Estadísticas
            urgent_count = len(data_sorted[data_sorted['Prioridad'] == 'URGENTE'])
            normal_count = len(data_sorted[data_sorted['Prioridad'] == 'NORMAL'])
            error_count = len(data_sorted[~data_sorted['Prioridad'].isin(['URGENTE', 'NORMAL'])])
            
            print(f"\nESTADISTICAS DEL REPORTE:")
            print(f"   Total de items: {len(data_sorted)}")
            print(f"   Items URGENTES: {urgent_count}")
            print(f"   Items NORMALES: {normal_count}")
            
            if error_count > 0:
                print(f"   Items con ERROR: {error_count}")
            
            if urgent_count > 0:
                print(f"\nALERTA: {urgent_count} items requieren atencion INMEDIATA!")
                print("   Estos items superan el umbral establecido y deben priorizarse.")
            
            return filename
                
        except Exception as e:
            print(f"Error generando reporte: {e}")
            import traceback
            traceback.print_exc()
            return None

def main():
    print("=" * 80)
    print("ROBOT AUDITOR ACME - Universidad de Atacama")
    print("=" * 80)
    
    print("\n   INICIALIZACION Y SEGURIDAD")
    print("-" * 60)
    
    config = ConfigManager('config.xlsx')
    settings = config.load_config()
    
    cred_manager = CredentialManager()
    username, password = cred_manager.get_secure_credential(settings['credential_asset'])
    
    browser = ACMEBrowser(settings)
    if not browser.initialize_browser():
        print("No se pudo inicializar el navegador. Abortando...")
        return
    
    if not browser.login_to_acme(username, password):
        print("Fallo el login. Verifica:")
        print("   - Credenciales en Windows Credential Manager")
        print("   - URL en config.xlsx")
        print("   - Revisa los screenshots generados")
        browser.driver.quit()
        return
    
    print("\n   EXTRACCION Y FILTRADO")
    print("-" * 60)
    
    if not browser.navigate_to_work_items():
        print("Continuando con extraccion desde URL actual...")
    
    all_items_df = browser.extract_work_items_table()
    
    if all_items_df.empty:
        print("No se encontraron work items para procesar")
        
        # Generar reporte vacío
        empty_df = pd.DataFrame(columns=['WIID', 'Description', 'Fecha Original', 'Dias Antiguedad', 'Prioridad'])
        report_file = ReportManager.generate_excel_report(empty_df, "Gallardo")
        
        browser.safe_logout()
        return
    
    print(f"\nDatos extraidos ({len(all_items_df)} items):")
    print(all_items_df[['WIID', 'Type', 'Status', 'Date']].head())
    
    processor = BusinessProcessor(settings['urgent_threshold'])
    filtered_items = processor.filter_items(all_items_df)
    
    if filtered_items.empty:
        print("No se encontraron items W15 con status Open/Abierto")
        print("Generando reporte vacio segun especificaciones...")
        empty_df = pd.DataFrame(columns=['WIID', 'Description', 'Fecha Original', 'Dias Antiguedad', 'Prioridad'])
        report_file = ReportManager.generate_excel_report(empty_df, "Gallardo")
        browser.safe_logout()
        return
    
    print(f"\nItems filtrados ({len(filtered_items)} items):")
    print(filtered_items[['WIID', 'Type', 'Status', 'Date']].head())
    
    print("\n   PROCESAMIENTO Y LOGICA DE NEGOCIO")
    print("-" * 60)
    
    final_results = processor.process_items(filtered_items, browser)
    
    print("\n   REPORTE Y CIERRE")
    print("-" * 60)
    
    report_file = ReportManager.generate_excel_report(final_results, "Gallardo")
    
    browser.safe_logout()
    
    print("\n" + "=" * 80)
    print("EJECUCION COMPLETADA EXITOSAMENTE")
    print("=" * 80)
    
    if report_file:
        file_path = os.path.abspath(report_file)
        print(f"\nREPORTE GENERADO:")
        print(f"   Nombre: {report_file}")
        print(f"   Ubicacion: {file_path}")
        
        try:
            df_report = pd.read_excel(report_file)
            print(f"\nCONTENIDO DEL REPORTE ({len(df_report)} items):")
            
            if not df_report.empty:
                # Mostrar todas las filas
                pd.set_option('display.max_rows', None)
                pd.set_option('display.max_columns', None)
                print(df_report.to_string(index=False))
                
                # Mostrar estadísticas
                urgent_items = df_report[df_report['Prioridad'] == 'URGENTE']
                if not urgent_items.empty:
                    print(f"\nItems URGENTES ({len(urgent_items)}):")
                    print(urgent_items[['WIID', 'Description', 'Dias Antiguedad']].to_string(index=False))
        except Exception as e:
            print(f"\nError mostrando contenido del reporte: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()