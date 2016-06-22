import os
import json

from tests import BaseTestCase
from app.api_1_0.game_resource import _result_str_valid, validate_game_submission
from app.api_1_0.api_exception import ApiException

# http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-vii-unit-testing
# http://flask.pocoo.org/docs/testing/#testing
# https://github.com/mjhea0/flaskr-tdd

class TestGameResource(BaseTestCase):

    games_endpoint = '/api/v1/games'
    good_queryparams = {
        'server_tok': 'secret_kgs',
        'b_tok': 'secret_foo_KGS',
        'w_tok': 'secret_bar_KGS',
    }
    good_bodyparams = {
        "black_id": 1,
        "white_id": 2,
        "game_server": "KGS",
        'rated': True,
        'result': 'B+0.5',
        'date_played': '2014-08-19T10:30:00',
        'game_record': '\n'.join(open('tests/testsgf.sgf').readlines())
    }

    expected_return = dict((k,v) for (k,v) in good_bodyparams.items() if k != 'game_record')

    def test_games_endpoint_success(self):
        create_response = self.client.post(
            self.games_endpoint,
            query_string=self.good_queryparams,
            data=json.dumps(self.good_bodyparams),
            headers={"Content-Type": "application/json"}
        )
        created_game = create_response.json
        for key, value in self.expected_return.items():
            self.assertEqual(value, created_game[key])
        self.assertEqual(create_response.status_code, 201)

        get_response = self.client.get(os.path.join(
            self.games_endpoint,
            str(created_game['id'])
        ))
        fetched_game = get_response.json
        self.assertEqual(fetched_game, created_game)
        self.assertEqual(get_response.status_code, 200)

        sgf_fetch_response = self.client.get(os.path.join(
            self.games_endpoint,
            str(created_game['id']),
            "sgf"
        ))

        self.assertEqual(
            sgf_fetch_response.headers['Content-Type'],
            'application/x-go-sgf'
        )
        self.assertEqual(sgf_fetch_response.data.decode('utf8'), self.good_bodyparams['game_record'])

    def test_games_endpoint_game_url(self):
        game_url = "http://files.gokgs.com/games/2015/3/3/Clutter-underkey.sgf"
        bodyparams = self.good_bodyparams.copy()
        bodyparams.pop("game_record")
        bodyparams['game_url'] = game_url
        r = self.client.post(self.games_endpoint, query_string=self.good_queryparams, data=json.dumps(bodyparams), headers={"Content-Type": "application/json"})
        actual = r.json
        for key, value in self.expected_return.items():
            self.assertEqual(value, actual[key])
        self.assertEqual(r.status_code, 201)

    def test_validate_missing_auth(self):
        for k in self.good_queryparams.keys():
            q = self.good_queryparams.copy()
            q.pop(k, None)  # on each iteration, remove 1 param
            with self.assertRaises(ApiException) as exception_context:
                validate_game_submission(q, self.good_bodyparams)
            self.assertIn(k, exception_context.exception.message)

    def test_validate_missing_params(self):
        for k in self.good_bodyparams.keys():
            q = self.good_bodyparams.copy()
            q.pop(k, None)  # on each iteration, remove 1 param
            with self.assertRaises(ApiException) as exception_context:
                validate_game_submission(self.good_queryparams, q)
            if k == 'game_record':
                expected = 'One of game_record or game_url must be present'
                self.assertEqual(expected, exception_context.exception.message)
            else:
                self.assertIn(k, exception_context.exception.message)

    def test_validate_bad_user_token(self):
        for param in ['w_tok', 'b_tok', 'server_tok']:
            # User token is bad
            q = self.good_queryparams.copy()
            q[param] = 'bad_tok'
            with self.assertRaises(ApiException) as exception_context:
                validate_game_submission(q, self.good_bodyparams)

            if param == 'server_tok':
                expected = 'server access token unknown or expired: bad_tok'
            else:
                expected = 'user access token unknown or expired: bad_tok'
            self.assertEqual(expected, exception_context.exception.message)

    def test_validate_rated(self):
        bodyparams = self.good_bodyparams.copy()
        for is_rated in [True, False]:
            bodyparams['rated'] = is_rated
            game = validate_game_submission(self.good_queryparams, bodyparams)
            self.assertEqual(game.rated, is_rated)

        bodyparams['rated'] = '0'
        with self.assertRaises(ApiException) as exception_context:
            validate_game_submission(self.good_queryparams, bodyparams)

        expected = 'rated must be set to True or False'
        self.assertEqual(expected, exception_context.exception.message)

    def test_validate_result(self):
        good_results = [
            'W+0.5', 'B+100',
            'B+0.5', 'B+42',
            'W+R', 'W+Resign', 'W+T', 'W+Time', 'W+F', 'W+Forfeit',
            'B+R', 'B+Resign', 'B+T', 'B+Time', 'B+F', 'B+Forfeit',
            'Void', '?', '0', 'Draw'
        ]
        bad_result = 'B+W'
        for result in good_results:
            self.assertTrue(_result_str_valid(result))
        self.assertFalse(_result_str_valid(bad_result))
