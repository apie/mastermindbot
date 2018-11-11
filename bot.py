#!/usr/bin/env python3
import emoji
import datetime
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler, CallbackQueryHandler
from random import shuffle
from settings import API_KEY
import high_score

DEFAULT_CODE_STYLE = 'hearts'
AANTAL_RONDES = 10

def set_high_score(user, rounds, duration):
    print('set_high_score')
    high_score.set_high_score(user.first_name, user.id, rounds, duration)

def show_high_scores(bot, update, query=None, user=None):
    print('show_high_scores')
    if not user:
      user = update.message.from_user
    high_scores = high_score.get_high_scores(user.id)
    print('high_scores ontvangen')
    reply_text = 'Uw top 5:\r\n%s' % "\r\n".join(['%s: %s' % (str(r['date']), r['score']) for r in high_scores['my_top'][:5]])
    print(reply_text)
    if query:
      query.message.reply_text(reply_text)
    else:
      update.message.reply_text(reply_text)
    reply_text = 'Algemene top 5:\r\n%s' % "\r\n".join(['%s: %s' % (str(r['user']), r['score']) for r in high_scores['global_top'][:5]])
    print(reply_text)
    if query:
      query.message.reply_text(reply_text)
    else:
      update.message.reply_text(reply_text)

def code_options():
    return dict(
      numbers=[str(n) for n in range(1,7)],
      hearts=[emoji.emojize(':red_heart:'), emoji.emojize(':yellow_heart:'), emoji.emojize(':green_heart:'), emoji.emojize(':blue_heart:'), emoji.emojize(':purple_heart:'), emoji.emojize(':black_heart:')],
      fruits=[emoji.emojize(':apple:', use_aliases=True), emoji.emojize(':lemon:'), emoji.emojize(':banana:'), emoji.emojize(':pineapple:'), emoji.emojize(':green_apple:'), emoji.emojize(':tangerine:')]
    )

def get_code_option(code_style):
    return code_options().get(code_style or DEFAULT_CODE_STYLE)

def new_code(code_style):
    code = get_code_option(code_style)
    assert len(code) == 6
    shuffle(code)
    return code[:4]  # return 4 items

def start(bot, update):
  logmessage(bot, update)
  update.message.reply_text('''Deze bot kan mastermind met u spelen.
De speler moet in tien beurten de code raden. De code bestaat uit een combinatie van 4 unieke kleuren harten. Er zijn 6 mogelijke kleuren.
Na het invoeren van vier harten heeft u uw beurt voltooid. De computer geeft nu aan hoeveel harten er zowel correct gevonden als geplaatst waren, en hoeveel er enkel correct gevonden waren.
Na tien beurten is het spel afgelopen.
Success! %s
Wilt u het potje halverwege afbreken? Geef dan /stoppen.
Geef /highscore om de records te zien.
Geef /code_style om de een ander type code in te stellen.
Geef /begin om te beginnen.
''' % emoji.emojize(':thumbsup:', use_aliases=True))

def get_reply_markup(code_style):
  reply_keyboard = [[InlineKeyboardButton(o, callback_data=o) for o in get_code_option(code_style)[:3]],
                    [InlineKeyboardButton(o, callback_data=o) for o in get_code_option(code_style)[-3:]],
                    [InlineKeyboardButton('Stop', callback_data='stop')],
                    ]
  reply_markup = InlineKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
  return reply_markup

def logmessage(bot, update):
  print('[%s] received (%s): %s' % (datetime.datetime.now().ctime(), update.message.from_user.first_name, update.message.text))

def set_code_style(bot, update, user_data):
    code_opt = code_options()
    reply_text = 'Kies een van de volgende stijlen:'
    reply_keyboard = [
      [InlineKeyboardButton(" ".join(code_opt[o]), callback_data=o) for o in sorted(code_opt.keys())]
    ]
    reply_markup = InlineKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(reply_text, reply_markup=reply_markup)

def start_round(bot, update, user_data, query=None):
    print('start_round')
    if user_data.get('user') is None:
      user_data['user'] = update.message.from_user
    if not query:
      user_data['code'] = new_code(user_data.get('code_style'))
      print('Code:')
      print(emoji.demojize(" ".join(user_data['code'])))
      user_data['started'] = datetime.datetime.now()
      user_data['ronde'] = 1
      user_data['guess'] = ''
   
    print('guess')
    print(user_data['guess'])
    questionmark = emoji.emojize(':question:', use_aliases=True)
    reply_text = '{fill}'.format(fill=4*questionmark)
    if query:
      query.message.reply_text(reply_text, reply_markup=get_reply_markup(user_data.get('code_style')))
    else:
      update.message.reply_text(reply_text, reply_markup=get_reply_markup(user_data.get('code_style')))

def end_round(user_data):
    del user_data['code']

def check_for_another_game(bot, update, user_data, query):
    bot.edit_message_reply_markup(reply_markup=[],
      chat_id=query.message.chat_id,
      message_id=query.message.message_id)
    if query.data == 'Ja':
      return start_round(bot, update, user_data, query)
    query.message.reply_text('Tot ziens.')
    return

def make_guess(bot, update, user_data):
    bot.answer_callback_query(update.callback_query.id)
    print('make_guess')
    query = update.callback_query
    if query.data == 'stop':
      bot.edit_message_reply_markup(reply_markup=[],
        chat_id=query.message.chat_id,
        message_id=query.message.message_id)
      query.message.reply_text('Afgebroken.')
      return end_round(user_data)
    elif 'Nog een potje' in query.message.text:
      return check_for_another_game(bot, update, user_data, query)
    elif query.message.text == 'Kies een van de volgende stijlen:':
      bot.edit_message_reply_markup(reply_markup=[],
        chat_id=query.message.chat_id,
        message_id=query.message.message_id)
      query.message.reply_text('Opgeslagen.')
      user_data['code_style'] = query.data
      return

    user_data['guess'] += query.data
    questionmark = emoji.emojize(':question:', use_aliases=True)
    reply_text = '{attempt}{fill}'.format(attempt=user_data['guess'], fill=(4-len(user_data['guess']))*questionmark)
    bot.edit_message_text(text=reply_text,
      chat_id=query.message.chat_id,
      message_id=query.message.message_id,
      reply_markup=get_reply_markup(user_data.get('code_style')))
    if len(user_data['guess']) < 4:
      return
    print('de opties binnen')
    bot.edit_message_reply_markup(reply_markup=[],
      chat_id=query.message.chat_id,
      message_id=query.message.message_id)

    #4 opties binnen
    # Controleren
    guess = user_data['guess']
    code = user_data['code']
    print(emoji.demojize(guess))
    goed = 0
    goede_kleur = 0
    for idx, itm in enumerate(guess):
      if itm == code[idx]:
        goed += 1
      elif itm in code:
        goede_kleur += 1

    resultaten = 'Goed: %s. Alleen kleur goed: %s. %s' % (goed, goede_kleur, emoji.emojize(':book:', use_aliases=True))
    print(resultaten)
    #resultaten bekend
    reply_text = emoji.emojize(':green_apple:', use_aliases=True)
    reply_text += 'Ronde %s:' % user_data['ronde']
    reply_text += ' '+resultaten
    query.message.reply_text(reply_text)

    if user_data['ronde'] < AANTAL_RONDES and goed < 4:
      #ronde afgelopen, niet gewonnen of verloren
      print('beurt afgelopen')
      user_data['guess'] = ''
      user_data['ronde'] += 1
      start_round(bot, update, user_data, query)
    else:
      print('spel afgelopen')
      if goed == 4:
        print('gewonnen')
        reply_text = 'Gewonnen! %s' % emoji.emojize(':muscle:', use_aliases=True)
        set_high_score(user_data['user'],
                       user_data['ronde'],
                       datetime.datetime.now()-user_data['started'])
      else:
        print('verloren')
        reply_text = 'Helaas, verloren. %s.\r\nDe code: %s.' % (emoji.emojize(':sob:', use_aliases=True), "".join(code))
      query.message.reply_text(reply_text)
      show_high_scores(bot, update, query, user_data['user'])
      end_round(user_data)
      nog_eens(bot, update, query)

def nog_eens(bot, update, query):
    reply_text = 'Nog een potje'
    reply_text += emoji.emojize(':question:', use_aliases=True)

    reply_keyboard = [[InlineKeyboardButton(o, callback_data=o) for o in ('Ja', 'Nee')]]
    reply_markup = InlineKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    if query:
      query.message.reply_text(reply_text, reply_markup=reply_markup)

def error(bot, update, error):
  logmessage(bot, update)
  print('error: %s' % error)
 
if __name__ == '__main__':
  updater = Updater(API_KEY)

  updater.dispatcher.add_handler(CommandHandler('start', start))
  updater.dispatcher.add_handler(CommandHandler('highscore', show_high_scores))
  updater.dispatcher.add_handler(CommandHandler('code_style', set_code_style, pass_user_data=True))

  updater.dispatcher.add_handler(CommandHandler('begin', start_round, pass_user_data=True))
  updater.dispatcher.add_handler(CallbackQueryHandler(make_guess, pass_user_data=True))

  updater.dispatcher.add_handler(MessageHandler(Filters.text, logmessage))
  updater.dispatcher.add_error_handler(error)

  print('bot gestart')
  updater.start_polling()
  updater.idle()

