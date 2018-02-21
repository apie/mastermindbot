#!/usr/bin/env python3
import emoji
import datetime
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
from random import shuffle
from settings import API_KEY
import high_score

AANTAL_RONDES = 10
BEURT, AFGELOPEN = range(2)

def set_high_score(user, rounds, duration=None):
    #TODO duration
    print('set_high_score')
    high_score.set_high_score(user.first_name, user.id, rounds, duration)

def show_high_scores(bot, update):
    logmessage(bot, update)
    print('show_high_scores')
    high_scores = high_score.get_high_scores(update.message.from_user.id)
    print('high_scores ontvangen')
    reply_text = 'Uw top 5:\r\n%s' % "\r\n".join(['%s: %s' % (str(r['date']), r['score']) for r in high_scores['my_top'][:5]])
    print(reply_text)
    update.message.reply_text(reply_text)
    reply_text = 'Algemene top 5:\r\n%s' % "\r\n".join(['%s: %s' % (str(r['user']), r['score']) for r in high_scores['global_top'][:5]])
    print(reply_text)
    update.message.reply_text(reply_text)

def code_options():
    return [emoji.emojize(':red_heart:'), emoji.emojize(':yellow_heart:'), emoji.emojize(':green_heart:'), emoji.emojize(':blue_heart:'), emoji.emojize(':purple_heart:'), emoji.emojize(':black_heart:')]

def new_code():
    code = code_options()
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
Geef /begin om te beginnen.
''' % emoji.emojize(':thumbsup:', use_aliases=True))

def logmessage(bot, update):
  print('[%s] received (%s): %s' % (datetime.datetime.now().ctime(), update.message.from_user.first_name, update.message.text))

def first_round(bot, update, user_data):
    reply_keyboard = [code_options()[:3], code_options()[-3:]]
    reply_text = emoji.emojize(':green_apple:', use_aliases=True)
    logmessage(bot, update)
    user_data['code'] = new_code()
    print(emoji.demojize(" ".join(user_data['code'])))
    user_data['ronde'] = 1
    user_data['guess'] = ''
    reply_text += 'Ronde: %s' % user_data['ronde']
    update.message.reply_text(reply_text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))
    return BEURT

def check_round(bot, update, user_data):
    reply_keyboard = [code_options()[:3], code_options()[-3:]]
    reply_text = emoji.emojize(':green_apple:', use_aliases=True)
    logmessage(bot, update)
    user_data['guess'] += update.message.text
    if len(user_data['guess']) < 4:
      return BEURT
    user_data['ronde'] += 1

    guess = user_data['guess']
    code = user_data['code']
    goed = 0
    goede_kleur = 0
    for idx, itm in enumerate(guess):
      if itm == code[idx]:
        goed += 1
      elif itm in code:
        goede_kleur += 1

    resultaten = 'Aantal goed: %s. Aantal goede kleur: %s. %s' % (goed, goede_kleur, emoji.emojize(':book:', use_aliases=True))
    print(resultaten)

    reply_text += resultaten
    if user_data['ronde'] <= AANTAL_RONDES and goed < 4:
        reply_text += '\r\nRonde: %s' % user_data['ronde']
        print('ronde: ',user_data['ronde'])
    update.message.reply_text(reply_text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))

    if user_data['ronde'] <= AANTAL_RONDES and goed < 4:
      user_data['guess'] = ''
      return BEURT
    else:
      if goed == 4:
        reply_text = 'Gewonnen! %s' % emoji.emojize(':muscle:', use_aliases=True)
        set_high_score(update.message.from_user,
                       user_data['ronde']-1)
      else:
        reply_text = 'Helaas, verloren. %s.\r\nDe code: %s.' % (emoji.emojize(':sob:', use_aliases=True), "".join(code))
      update.message.reply_text(reply_text,
                                reply_markup=ReplyKeyboardRemove())
      user_data['ronde'] = 1
      show_high_scores(bot, update)
      return vraag_nog_eens(bot, update)

def vraag_nog_eens(bot, update):
    logmessage(bot, update)
    reply_keyboard = [['Ok', 'Nee']]

    reply_text = 'Nog een potje%s' % emoji.emojize(':question:', use_aliases=True)
    update.message.reply_text(
        reply_text,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return AFGELOPEN

def nog_eens(bot, update, user_data):
    if update.message.text == 'Nee':
        return cancel(bot, update)
    elif update.message.text == 'Ok':
        return first_round(bot, update, user_data)

def end_game(bot, update, user_data):
    print('in end_game')
    update.message.reply_text('Dat was het!',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def cancel(bot, update):
    print('in cancel')
    user = update.message.from_user
    print("User %s canceled the conversation." % user.first_name)
    update.message.reply_text('Tot ziens.',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def error(bot, update, error):
  logmessage(bot, update)
  print('error: %s' % error)
 
if __name__ == '__main__':
  updater = Updater(API_KEY)
  hearts = "|".join(code_options())

  updater.dispatcher.add_handler(CommandHandler('start', start))
  updater.dispatcher.add_handler(CommandHandler('highscore', show_high_scores))
  conv_handler = ConversationHandler(
      entry_points=[CommandHandler('begin', first_round, pass_user_data=True)],
      states={
          BEURT: [RegexHandler('^(%s)$' % hearts, check_round, pass_user_data=True)],
          AFGELOPEN: [RegexHandler('^(Ok|Nee)$', nog_eens, pass_user_data=True)]
      },
      fallbacks=[CommandHandler('stoppen', cancel)],
      allow_reentry=True
  )
  updater.dispatcher.add_handler(conv_handler)

  updater.dispatcher.add_handler(MessageHandler(Filters.text, logmessage))

  updater.dispatcher.add_error_handler(error)

  updater.start_polling()
  updater.idle()

