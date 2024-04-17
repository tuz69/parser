import requests
import json
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageOps
import io
def parse_page(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage {url}. Status code: {response.status_code}")
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    # Находим блок 'container-row clearfix container-wrap'
    container_wrap = soup.find('div', class_='container-row clearfix container-wrap')
    if not container_wrap:
        print(f"Не удалось найти блок с классом 'container-row clearfix container-wrap' на странице {url}")
        return None
    # Находим блок 'container-left' внутри 'container-wrap'
    container_left = container_wrap.find('div', class_='container-left')
    if not container_left:
        print(f"Не удалось найти блок с классом 'container-left' на странице {url}")
        return None
    # Находим секцию 'section-page-white' внутри 'container-left'
    section = container_left.find('section', class_='section-page-white')
    if not section:
        print(f"Не удалось найти секцию с классом 'section-page-white' на странице {url}")
        return None
    # Находим список 'pdt-list-ul' внутри 'section-page-white'
    ul = section.find('ul', class_='pdt-list-ul')
    if not ul:
        print(f"Не удалось найти список с классом 'pdt-list-ul' на странице {url}")
        return None
    titles_and_images = []
    img_count = 1
    li_elements = ul.find_all('li')
    for idx, li in enumerate(li_elements):
        # Парсинг заголовка h3 внутри 'li'
        h3 = li.find('h3', class_='pdt-list-h3')
        if h3:
            a_tag = h3.find('a')
            if a_tag and a_tag.text:
                title = a_tag.text.strip()
                # Парсинг изображения
                next_li = li_elements[idx + 1] if idx + 1 < len(li_elements) else None
                img_container = next_li.find('a', class_='pdt-list-img') if next_li else None
                if img_container:
                    img_tag = img_container.find('img')
                    img_url = img_tag['data-original'] if img_tag and 'data-original' in img_tag.attrs else None
                    if img_url:
                        img_name = f"{img_count}.png"
                        img_count += 1
                        # Определение формата изображения
                        img_extension = re.search(r'\.([a-zA-Z]+)$', img_url)
                        if img_extension:
                            img_extension = img_extension.group(1)
                            img_name = f"{img_count}.{img_extension}"
                            img_count += 1
                        titles_and_images.append({
                            "title": title,
                            "img": img_url,
                            "description": "TextDescr"
                        })
    return titles_and_images
def main():
    root = tk.Tk()
    root.title("HappyMod Parser")
    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    base_url_label = ttk.Label(frame, text="Введите базовую страницу:")
    base_url_label.grid(row=0, column=0, sticky=tk.W, pady=5)
    base_url_entry = ttk.Entry(frame, width=50)
    base_url_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
    start_page_label = ttk.Label(frame, text="Введите начальную страницу:")
    start_page_label.grid(row=1, column=0, sticky=tk.W, pady=5)
    start_page_entry = ttk.Entry(frame, width=10)
    start_page_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
    end_page_label = ttk.Label(frame, text="Введите конечную страницу:")
    end_page_label.grid(row=2, column=0, sticky=tk.W, pady=5)
    end_page_entry = ttk.Entry(frame, width=10)
    end_page_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
    img_width_label = ttk.Label(frame, text="Ширина:")
    img_width_label.grid(row=3, column=0, sticky=tk.W, pady=5)
    img_width_entry = ttk.Entry(frame, width=10)
    img_width_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
    img_height_label = ttk.Label(frame, text="Высота:")
    img_height_label.grid(row=4, column=0, sticky=tk.W, pady=5)
    img_height_entry = ttk.Entry(frame, width=10)
    img_height_entry.grid(row=4, column=1, sticky=tk.W, pady=5)
    def run_parser():
        base_url = base_url_entry.get()
        start_page = int(start_page_entry.get())
        end_page = int(end_page_entry.get())
        img_width = int(img_width_entry.get())
        img_height = int(img_height_entry.get())
        all_data = []
        for page_number in range(start_page, end_page + 1):
            url = urljoin(base_url, f"{page_number}/")
            data = parse_page(url)
            if data is None:
                break
            all_data.extend(data)
        file_name = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")], title="Введите имя файла для сохранения JSON-файла")
        save_folder = filedialog.askdirectory(title="Укажите путь для сохранения файла")
        img_save_folder = filedialog.askdirectory(title="Укажите путь для сохранения папки изображений")
        save_path = os.path.join(save_folder, file_name.split('/')[-1])
        img_folder = os.path.join(img_save_folder, "images")
        if not os.path.exists(img_folder):
            os.makedirs(img_folder)
        with open(save_path, 'w', encoding='utf-8') as file:
            json.dump(all_data, file, ensure_ascii=False, indent=4)
        # Сохранение изображений
        for data in all_data:
            img_url = data.get("img")
            img_name = os.path.join(img_folder, os.path.basename(img_url))
            response = requests.get(urljoin(base_url, img_url))
            if response.status_code == 200:
                try:
                    img = Image.open(io.BytesIO(response.content)).convert("RGB")
                    img = img.resize((img_width, img_height), Image.ANTIALIAS)
                    img.save(img_name)
                except Exception as e:
                    print(f"Error processing image {img_name}: {e}")
        messagebox.showinfo("Success", f"Заголовки и изображения сохранены в файл: {save_path}")
    run_button = ttk.Button(frame, text="Запустить", command=run_parser)
    run_button.grid(row=5, columnspan=2, pady=10)
    root.mainloop()
if __name__ == '__main__':
    main()
