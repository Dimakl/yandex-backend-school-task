# yandex-backend-school-task
Python REST API сервис для второго вступительного задания в школу Яндекс 

## Установка (для linux):
Проект запакован в докер. Если у вас не он не установлен:
```
sudo apt-get remove docker docker-engine docker.io containerd runc

sudo apt-get update

sudo apt-get install apt-transport-https ca-certificates curl gnupg lsb-release

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update

sudo apt install apt-transport-https ca-certificates curl software-properties-common

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

sudo add-apt-repository "deb [arch=amd64]

https://download.docker.com/linux/ubuntu bionic test" sudo apt update sudo

apt install docker-ce
```


Если у вас не установлен docker-compose:
```
sudo apt install jq

VERSION=$(curl --silent https://api.github.com/repos/docker/compose/releases/latest | jq .name -r)

DESTINATION=/usr/local/bin/docker-compose sudo curl -L https://github.com/docker/compose/releases/download/${VERSION}/docker-compose-$(uname -s)-$(uname -m) -o $DESTINATION sudo chmod 755 $DESTINATION
```

Установка и запуск контейнера с проектом:
```
git clone https://github.com/Dimakl/yandex-backend-school-task

cd yandex-backend-school-task/

sudo docker-compose up  --build -d
```

Все, проект установлен и работает, после ребута он также перезагрузится, чтобы проверить что он стоит можно кинуть этот запрос:
```
curl 'http://127.0.0.1:8080/couriers/0'
```

## Реализованные фичи из дополнительного оценнивания:

  - [X] Наличие реализованного обработчика  6: GET /couriers/$courier_id 
  > Обработчик пристствует!
  - [X] Наличие структуры с подробным описанием ошибок каждого некорректного поля, пришедшего в запросе
  > В каждом случае, когда это требуется в поле "errors_description" в json ответе приходит полное описание всех некорректных полей или других ошибок.
  - [X] Явно описанные внешние python-библиотеки (зависимости)
  > В requirements.txt описаны все зависимости проекта.
 - [ ] Наличие тестов
  > Тесты к сожалению написать не успел, слишком поздно узнал об отборе :)
 - [X] Наличие файла  README  в корне репозитория с инструкциями по установке, развертыванию и запуску сервиса и
тестов
  > Вот он!
 - [X] Автоматическое возобновление работы REST API после перезагрузки виртуальной машины
  > Контейнер автоматически разворачивается заново после каждого ребута.
 - [X] Возможность обработки нескольких запросов сервисом одновременно
  > Я не уверен что это на самом деле работает, но в gunicorn работают 3 воркера, поэтому вроде как несколько запросов обрабатывать одновременно получится.
