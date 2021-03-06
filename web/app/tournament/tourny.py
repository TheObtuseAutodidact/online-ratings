
import datetime
from flask import current_app, render_template, redirect, url_for
from flask import jsonify, request, Response
from . import tournament
from app.forms import TournamentForm, TournamentPlayerForm
from app.models import db, Tournament, TournamentPlayer
from sqlalchemy import update

@tournament.route('/', methods=['GET', 'POST'])
def index():
    form = TournamentForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            t = Tournament(event_name=form.event_name.data,
                           venue=form.venue.data,
                           venue_address=form.venue_address.data,
                           venue_state=form.venue_state.data,
                           venue_zip=form.venue_zip.data,
                           start_date=form.start_date.data,
                           end_date=form.end_date.data,
                           director=form.director.data,
                           director_phone=form.director_phone.data,
                           director_email=form.director_email.data,
                           director_address=form.director_address.data,
                           sponsor=form.sponsor.data,
                           sponsor_phone=form.sponsor_phone.data,
                           sponsor_email=form.sponsor_email.data,
                           sponsor_website=form.sponsor_website.data,
                           sponsor_address=form.sponsor_address.data,
                           convener=form.convener.data,
                           convener_phone=form.convener_phone.data,
                           convener_email=form.convener_email.data,
                           convener_website=form.convener_website.data,
                           convener_address=form.convener_address.data,
                           pairing=form.pairing.data,
                           rule_set=form.rule_set.data,
                           time_controls=form.time_controls.data,
                           basic_time=form.basic_time.data,
                           overtime_format=form.overtime_format.data,
                           overtime_conditions=form.overtime_conditions.data,
                           komi=form.komi.data,
                           tie_break1=form.tie_break1.data,
                           tie_break2=form.tie_break2.data,
                           submitted=form.submitted.data)
            db.session.add(t)
            db.session.commit()
            # flash("Tournament successfully created.")
            return redirect(url_for('.index'))
    tournaments = Tournament.query.all()
    return render_template('tournament_index.html', tournaments=tournaments)

@tournament.route('/<int:tournament_id>/', methods=['GET', 'POST',
                                                'PUT', 'DELETE'])
def show(tournament_id):
    tournament = Tournament.query.get(tournament_id)
    if tournament:
        if request.method == "GET":
            return render_template('tournament_show.html',
                tournament=tournament)
        elif request.method != "GET" and tournament.submitted == False:
            method = request.form.get('_method', '').upper()
            if method:
                if tournament.submitted == False:
                    if method == "DELETE":
                        db.session.delete(tournament)
                        db.session.commit()
                        # flash('{{ tournament.event_name }} has been deleted')
                        return redirect(url_for('.index'))
                    elif method == "PUT":
                        form = TournamentForm(obj=tournament)
                        if form.validate_on_submit():
                            form.populate_obj(tournament)
                            db.session.commit()
                            # flash("Tournament successfully edited.")
                            return redirect(url_for('.show',
                                tournament_id=tournament_id))
                # flash("Cannot alter submitted record")
                return redirect(url_for('.index'))
        else:
            # flash("Cannot alter submitted record")
            return redirect(url_for('.index'))
    else:
        # flash('Tournament id {{ tournament_id }} does not exist.')
        return redirect(url_for('.index'))

@tournament.route('/new/', methods=['GET'])
def new_tournament():
    form = TournamentForm()
    return render_template('tournament_form.html', form=form)


@tournament.route('/<int:tournament_id>/edit/', methods=['GET'])
def edit_tournament(tournament_id):
    tournament = Tournament.query.get(tournament_id)
    form = TournamentForm(obj=tournament)
    return render_template('tournament_form.html',
                            form=form, tournament=tournament)

@tournament.route('/<int:tournament_id>/players/', methods=["GET", "POST"])
def players_index(tournament_id):
    tournament = Tournament.query.get(tournament_id)
    if tournament and tournament.submitted == False:
        form = TournamentPlayerForm()
        if request.method == 'POST' and form.validate_on_submit(): #  consider a vanity url for posting
                #  if before first_round  - a cutoff for adding new players
            tp = TournamentPlayer(tournament_id = tournament_id,
                                 name = form.name.data,
                                 aga_num = form.aga_num.data,
                                 rating = form.rating.data,
                                 affiliation = form.affiliation.data,
                                 state = form.state.data,
                                 address = form.address.data,
                                 email = form.email.data,
                                 phone = form.phone.data,
                                 citizenship = form.citizenship.data,
                                 dob = form.dob.data)
            db.session.add(tp)
            db.session.commit()
                # flash("Player {{ tp.name }} successfully added")
            return redirect(url_for('.new_player', tournament_id=tournament_id))
        elif tournament.submitted == True:
            #  flash(Cannot alter submitted reccord)
            return redirect(url_for('.index'))

        players = TournamentPlayer.query.filter_by(tournament_id=tournament_id)
        tournament = Tournament.query.get(tournament_id)
        return render_template("tournament_players_index.html", players=players,
        tournament=tournament)
    else:
        # flash("No tournament record found")
        return redirect(url_for('.index'))


@tournament.route('/<int:tournament_id>/player/new/', methods=["GET"])
def new_player(tournament_id):
    form = TournamentPlayerForm()
    tournament = Tournament.query.get(tournament_id)
    return render_template('tournament_player_form.html', form=form,
        tournament=tournament)


@tournament.route('/<int:tournament_id>/player/<int:tournament_player_id>/',
    methods=["GET", "POST", "PUT", "DELETE"]) # add PUT
def select_player(tournament_id, tournament_player_id):
    tournament = Tournament.query.get(tournament_id)
    tp = TournamentPlayer.query.get(tournament_player_id)
    method = request.form.get('_method', '').upper()
    if tournament and tp and tournament.submitted == False:
        if request.method == "GET":
            form = TournamentPlayerForm(obj=tp)
            return render_template('tournament_player_form.html',
                form=form, tournament=tournament, tp=tp)
        if method == 'DELETE':
            db.session.delete(tp)
            db.session.commit()
            # flash("{{ tp.name }} has been deleted from" +
            #     "{{ tp.tournament.event_name}}")
            return redirect(url_for('.players_index',
                tournament_id=tournament_id))
        if method == "PUT":
            form = TournamentPlayerForm(obj=tp)
            if form.validate_on_submit():
                form.populate_obj(tp)
                db.session.commit()
                return redirect(url_for('.players_index',
                    tournament_id=tournament_id))
    else:
        # flash("Could not delete player: {{ tp.name }}")
        return redirect(url_for('.players_index',
            tournament_id=tournament_id))
