import datetime


products = {
    'TV': {
        'metaData': {
            'id': 'prod1',
            'lastUpdated': datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M:%S %p"),
            'name': 'TV'
        },
        'analyticData': {
            'sentimentData': [
                {
                    'name': 'Amazon',
                    'data': {
                        'positive': 10,
                        'negative': 11,
                        'neutral': 5
                    }
                },
                {
                    'name': 'Home Depot',
                    'data': {
                        'positive': 5,
                        'negative': 25,
                        'neutral': 10
                    }
                }
            ]
        }
    },
    'Radio': {
        'metaData': {
            'id': 'prod2',
            'lastUpdated': datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M:%S %p"),
            'name': 'Radio'
        },
        'analyticData':{
            'sentimentData': [
                {
                    'name': 'Amazon',
                    'data': {
                        'positive': 10,
                        'negative': 11,
                        'neutral': 5
                    }
                },
                {
                    'name': 'Home Depot',
                    'data': {
                        'positive': 5,
                        'negative': 25,
                        'neutral': 10
                    }
                }
            ]
        }
    },
    'Hot Plate': {
        'metaData': {
            'id': 'prod3',
            'lastUpdated': datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M:%S %p"),
            'name': 'Hot Plate'
        },
        'analyticData': {

        }
    },
}
