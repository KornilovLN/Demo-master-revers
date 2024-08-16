## Demo работы sunpp

#### Структура проекта и запуск

**_Структура_**
<br>Дерево проекта в можно посмотреть в файле
<br>**tree.txt**

**_Запуск контейнера проекта 'demo'_**
```
docker-compose -p demo up -d
```

**_При этом задействован docker-compose.yaml в корне 'demo'_**
<br>Что будет отработано:
* версия docker-composer - 3.2
* cоздан (volumes: data: driver: local)
* Sevices:
  <br>**meta** 
  <br>**www**

**_--------- meta -----------------------------------------------------------_**
<br> Сервис meta - запускается в фоновом режиме
<br> Образ должен быть по адресу **demo/ekatra**
<br> Контейнер с названием **demo-meta**  hostname **meta**
<br> В контейнере **demo-meta** будет запущена виртуальная машина **Virtuoso**
<br> Environment: IMAGE_TAG: '18.03.02'
<br> Логи driver: "json-file"

**_--------- www ------------------------------------------------------------_**
<br> Сервис www - запускается в фоновом режиме
<br> Образ должен быть по адресу **demo/ekatra**
<br> Контейнер с названием **demo-www**  hostname **www**
<br> В контейнере **demo-www** будет запущена **'/usr/local/bin/start_ekatra.sh'**
<br> Environment: IMAGE_TAG: '18.03.02'
<br> Логи driver: "json-file"
<br> Тома:
``` volumes:
      - '../backend/src/ekatra/backend:/usr/local/lib/python2.7/dist-packages/ekatra/backend'
      - '../rtdb/packages/rtdbsio/rtdbsio:/usr/local/lib/python2.7/dist-packages/rtdbsio'
      - 'data:/var/ekatra/'
```
<br> Порты: 8088:80 (8088-внешний, 80-внутренний порт) -> localhost:8088 

#### Описание coolie.yaml

**_Описание файла coolie.yaml_**
<br>Файл coolie.yaml является конфигурационным файлом, который используется для автоматизации различных задач в проекте. Он определяет настройки для Ansible и DoIt, а также описывает несколько целей (targets), каждая из которых представляет собой отдельную задачу или шаг в процессе сборки и развертывания проекта. Эти цели включают создание базового образа Docker, выполнение различных скриптов, обновление базы данных и подготовку данных для демонстрации.

**_Описание секции Ansible и DoIt конфигурация в coolie.yaml_**
```
ansible_config:
    verbosity: 1

doit_config:
    backend: sqlite3
    verbosity: 2
```    
<br>
- **ansible_config**:
  <br> Эта секция задает конф. Ansible, инструмента автоматизации управления конфигурацией.
  <br> **Параметр verbosity**: 1 указывает уровень подробности вывода Ansible.
- **doit_config**:
  <br> Эта секция задает конфигурацию для DoIt, инструмента для автоматизации задач.
  <br> **Параметр backend**: sqlite3 указывает, что DoIt будет использовать SQLite базу данных для хранения состояния задач. 
  <br> **Параметр verbosity**: 2 указывает уровень подробности вывода DoIt.

**_Описание секции vars в coolie.yaml_**
```
vars:
   VIRTUOSO_VERSION: 7.2.4.2
   NGINX_VERSION: 1.10.3
```    
<br>
- **vars**: Эта секция определяет переменные, которые будут использоваться в других частях конфигурационного файла.
- Например, VIRTUOSO_VERSION и NGINX_VERSION задают версии для Virtuoso и Nginx соответственно.

**_Описание цели baseimage в coolie.yaml_**
```
targets:
  - name: baseimage
    make_image:
      base: 'registry.master.cns/u16py2/virtuoso-client:{{ VIRTUOSO_VERSION }}'
      target: demo/base
    run:
      - playbook: coolie/baseimage.yaml
```    
<br>
- **name: baseimage**: Имя цели.
- **make_image**: Эта секция описывает создание Docker-образа.
  <br>base указывает базовый образ, который будет использоваться,
  <br>а target указывает имя создаваемого образа.
- **run**: секция указывает: После созд. образа выполнится Ansible playbook coolie/baseimage.yaml.

**_Описание step1 в coolie.yaml_**
```
  ... 
  - name: step1
    doc: "Step 1: Copy file and meta form znpp. Extract messages to .pot"
    make:
      - .work/demo.ttl
      - .work/nav.yaml
      - .work/spd/meta/mofstates.json
      - .work/spd/nav.json
    user: me
    onimage: registry.master.cns/u16py2/compiler
    working_dir: /build
    network: znpp
    volumes:
      znpp-var-data: /var/ekatra
      znpp-rtdb-data: /rtdb
    run:
      - shell: python -W ignore ./scripts/import_from_znpp.py
```
<br>
- **name: step1**: Имя цели.
- **doc**: Описание цели.
- **make**: Список файлов, которые должны быть созданы в результате выполнения этой цели.
- **user**: Пользователь, от имени которого будет выполняться задача.
- **onimage**: Docker-образ, который будет использоваться для выполнения задачи.
- **working_dir**: Рабочая директория внутри контейнера.
- **network**: Сеть, к которой будет подключен контейнер.
- **volumes**: Монтируемые тома.
- **run**: Команды внутри контейнера. В данном случае это import_from_znpp.py.
 
**_Описание step2 в coolie.yaml_**
```
  ... 
  - name: step2
    doc: "Step 2: Update rtdb by initial values"
    make: .work/rtdb_updated.txt
    assets:
      - name: rtdb_map
        make: .work/rtdb_map.yaml
        file_dep:
        - dump/rtdb.yaml
        - .work/demo.ttl
        user: me
        onimage: registry.master.cns/u16py2/compiler
        working_dir: /build
        run:
        - shell: python2 ./scripts/rtdb_map.py
    user: me
    onimage: registry.master.cns/u16py2/rtdb
    working_dir: /build
    run:
    - shell: python2 ./scripts/rtdb_push.py
    - shell: touch .work/rtdb_updated.txt

```
<br>
- **name: step2**: Имя цели.
- **doc**: Описание цели.
- **make**: Файл, который должен быть создан в результате выполнения этой цели.
- **assets**:  Доп. задачи, кот. должны быть выполнены.
  <br>В данном случае это создание файла rtdb_map.yaml.
- **user**: Пользователь, от имени которого будет выполняться задача.  
- **onimage**: Docker-образ, который будет использоваться для выполнения задачи.
- **working_dir**: Рабочая директория внутри контейнера.
- **network**: Сеть, к которой будет подключен контейнер.
- **run**: Команды, которые будут выполнены внутри контейнера.
  <br>В данном случае выполнение скриптов rtdb_map.py и rtdb_push.py.
 
**_Описание step3 в coolie.yaml_**
```
  ... 
  - name: step3
    doc: "Step 3: Translate to english"
    make:
    - .work/demo_en.ttl
    - .work/spd/en/nav.json
    - .work/spd/en/meta/mofstates.json
    file_dep:
    - translations/en/LC_MESSAGES/messages.po
    - .work/demo.ttl
    - .work/nav.yaml
    - .work/spd/meta/mofstates.json
    user: me
    onimage: registry.master.cns/u16py2/compiler
    working_dir: /build
    run:
    - shell: python2 ./scripts/tr_compile.py
```
<br>
- **name: step3**: Имя цели.
- **doc**: Описание цели.
- **make**: Файл, который должен быть создан в результате выполнения этой цели.
- **file_dep**: Список файлов, от которых зависит выполнение этой цели.
- **user**: Пользователь, от имени которого будет выполняться задача.  
- **onimage**: Docker-образ, который будет использоваться для выполнения задачи.
- **working_dir**: Рабочая директория внутри контейнера.
- **network**: Сеть, к которой будет подключен контейнер.
- **run**: Команды, которые будут выполнены внутри контейнера.
  <br>В данном случае выполнение скрипта tr_compile.py. 

**_Описание step4 в coolie.yaml_**
```
  ... 
  - name: step4
    doc: "Step 4: Prepare data for meta"
    make:
    - .work/meta-data.tgz
    onimage: 'registry.master.cns/u16py2/virtuoso:{{ VIRTUOSO_VERSION }}'
    working_dir: /build
    mounts:
      '/var/ekatra/meta': '.work/meta'
    run:
      - playbook: coolie/meta_db.yaml
```
<br>
- **name: step4**: Имя цели.
- **doc**: Описание цели.
- **make**: Файл, который должен быть создан в результате выполнения этой цели. 
- **onimage**: Docker-образ, который будет использоваться для выполнения задачи.
- **working_dir**: Рабочая директория внутри контейнера.
- **mounts**: Тома, которые будут смонтированы в контейнере.
- **run**: Команды, которые будут выполнены внутри контейнера.
  <br>В данном случае это выполнение Ansible playbook coolie/meta_db.yaml. 

**_Описание step5 в coolie.yaml_**
```
  ... 
  - name: step5
    doc: "Step 5: Prepare data for demo"
    make:
    - .work/ekatra-data.tgz
    run:
      - playbook: coolie/prepare_data.yaml
```
<br>
- **name: step5**: Имя цели.
- **doc**: Описание цели.
- **make**: Файл, который должен быть создан в результате выполнения этой цели. 
- **run**: Команды, которые будут выполнены внутри контейнера.
  <br>В данном случае это выполнение Ansible playbook coolie/prepare_data.yaml.

**_Описание step6 в coolie.yaml_**
```
  ... 
  - name: step6
    doc: "Step 6: Build image"
    make_image:
      base: demo/base
      target: demo/ekatra
    run:
      - playbook: coolie/image.yaml
```
<br>
- **name: step5**: Имя цели.
- **doc**: Описание цели.
- **make_image**: Эта секция описывает создание Docker-образа.
  <br>base указывает базовый образ, который будет использоваться, а
  <br>target указывает имя создаваемого образа.
- **run**: Команды, которые будут выполнены внутри контейнера.
  <br>В данном случае это выполнение Ansible playbook coolie/image.yaml.  

**_Описание kube в coolie.yaml_**
```
  ... 
  - name: kube
    vars:
      old_tag: 18.02.02
      new_tag: 18.02.03c
    make:
    - .work/a.txt
    run:
      - playbook: coolie/kube.yaml
```
<br>
- **name: step5**: Имя цели.
- **vars**:  Переменные, используемые в этой цели.
  <br>Например, old_tag и new_tag задают старую и новую версии тегов.
- **make**: Файл, который должен быть создан в результате выполнения этой цели.
- **run**: Команды, которые будут выполнены внутри контейнера.
  <br>В данном случае это выполнение Ansible playbook coolie/kube.yaml.  

#### Заключение
<br>Файл coolie.yaml описывает различные задачи, необходимые для сборки и развертывания проекта.
<br>Каждая цель включает в себя:
- описание задачи,
- зависимости,
- команды для выполнения
- и другие параметры: _пользователь_, _Docker-образ_ и _рабочая директория_.
<br>Этот файл автоматизирует процесс сборки и развертывания.   