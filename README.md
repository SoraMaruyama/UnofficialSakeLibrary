# Sake Library

Sake Library is the only sake database in the world.

<p align="center">

  <img src="https://raw.githubusercontent.com/SoraMaruyama/UnofficialSakeLibrary/master/readmeasset/home1.png">
  <img src="https://raw.githubusercontent.com/SoraMaruyama/UnofficialSakeLibrary/master/readmeasset/sakelist1.png">
  <img src="https://raw.githubusercontent.com/SoraMaruyama/UnofficialSakeLibrary/master/readmeasset/addsake1.png">
</p>

## API EndPoints

#### ./api/sakes => GET

This endpoint provides the list of sakes available in the Japan in a JSON Format
This Endpoint does not accept any parameter

Json Response:

```json
[
  {
    "id": "P00000001",
    "name": "Tenjin Bayashi Sake",
    "name_ja": "月桂冠",
    "type": "Junmai Ginjo",
    "type_ja": "純米吟醸",
    "is_fruity": "False",
    "maker": "Uonuma Sake Brewery",
    "maker_ja": "魚沼酒造",
    "region": "Kyoto",
    "region_ja": "京都府",
    "url": "https://www.sake-tour.jp/uonuma/?hl=en",
    "description": "",
    "description_ja": "",
    "image": "tenjin_bayashi_junmai_ginjo_front_1024x.jpg"
  }
]
```

#### ./api/id => GET

This Endpoint does accept a sigle parameter 'id' and return a fixed JSON object: - "sake" => the sake matches to the id

Ex:

```json
[
  {
    "id": "P00000001",
    "name": "Tenjin Bayashi Sake",
    "name_ja": "月桂冠",
    "type": "Junmai Ginjo",
    "type_ja": "純米吟醸",
    "is_fruity": "False",
    "maker": "Uonuma Sake Brewery",
    "maker_ja": "魚沼酒造",
    "region": "Kyoto",
    "region_ja": "京都府",
    "url": "https://www.sake-tour.jp/uonuma/?hl=en",
    "description": "",
    "description_ja": "",
    "image": "tenjin_bayashi_junmai_ginjo_front_1024x.jpg"
  }
]
```

### Prerequisites

What things you need to install the software and how to install them

```
python 3.7.10
pip
```

### Installing

How to get a development env running

```
pip install requirements.txt
```

## Built With

- [Flask](http://flask.pocoo.org/) - The web framework used
- [Pip](https://maven.apache.org/) - Dependency Management
- [Jinja 2.10](http://jinja.pocoo.org/docs/2.10/) - template engine work with Flask
- [Bootstrap 3.3](https://getbootstrap.com/docs/3.3/) - Design Frontend

## Authors

- **Sora Maruyama**
