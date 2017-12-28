#!/usr/bin/env python3
import emoji
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
from random import shuffle
from settings import API_KEY

BEURT = range(1)

def code_options():
    return [emoji.emojize(':red_heart:'), emoji.emojize(':yellow_heart:'), emoji.emojize(':green_heart:'), emoji.emojize(':blue_heart:'), emoji.emojize(':purple_heart:'), emoji.emojize(':black_heart:')]

def new_code():
    code = code_options()
    shuffle(code)
    return code[:4]  # return 4 items

def start(bot, update):
  print('received (%s): %s' % (update.message.from_user.first_name, update.message.text))
  update.message.reply_text('''Deze bot kan mastermind met je spelen.
De speler moet in tien beurten de code raden. De code bestaat uit een combinatie van 4 unieke kleuren. Er zijn 6 mogelijke kleuren.
De kleuren worden als de getallen 1 t/m 6 getoond. Het invoeren moet dus ook op basis van getallen.
Na het invoeren van vier kleuren heeft u uw beurt voltooid. De computer geeft nu aan hoeveel kleuren er zowel correct gevonden als geplaatst waren, en hoeveel er enkel correct gevonden waren.
Na tien beurten is het spel afgelopen.
Success! %s
Geef /begin om te beginnen.
''' % emoji.emojize(':thumbsup:', use_aliases=True))

def logmessage(bot, update, job_queue, chat_data):
  print('received (%s): %s' % (update.message.from_user.first_name, update.message.text))

def begin(bot, update):
    print('received (%s): %s' % (update.message.from_user.first_name, update.message.text))
    reply_keyboard = [['Ok', 'Nee']]

    reply_text = 'Zal ik het spel starten%s\r\nGeef /stoppen om te annuleren.' % emoji.emojize(':question:', use_aliases=True)
    update.message.reply_text(
        reply_text,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return BEURT

def check_round(bot, update, user_data):
    reply_keyboard = [code_options()[:3], code_options()[-3:]]
    reply_text = emoji.emojize(':green_apple:', use_aliases=True)
    print('received (%s): %s' % (update.message.from_user.first_name, update.message.text))
    if update.message.text == 'Nee':
      return cancel(bot, update)
    elif update.message.text == 'Ok':
      user_data['code'] = new_code()
      user_data['ronde'] = 1
      user_data['guess'] = ''
      reply_text += 'Ronde: %s' % user_data['ronde']
      update.message.reply_text(reply_text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))
    else:
      user_data['guess'] += update.message.text
    if len(user_data['guess']) < 4:
      return BEURT
    user_data['ronde'] += 1

    guess = user_data['guess']
    code = user_data['code']
    print(code)
    goed = 0
    goede_kleur = 0
    for idx, itm in enumerate(guess):
      if itm == code[idx]:
        goed += 1
      elif itm in code:
        goede_kleur += 1

    resultaten = 'Aantal goed: %s. Aantal goede kleur: %s. %s' % (goed, goede_kleur, emoji.emojize(':book:', use_aliases=True))
    print(resultaten)

    reply_text += 'Ronde: %s' % user_data['ronde']
    reply_text += '\r\n'+resultaten
    update.message.reply_text(reply_text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))

    print('ronde: ',user_data['ronde'])
    if user_data['ronde'] < 10 and goed < 4:
      user_data['guess'] = ''
      return BEURT
    else:
      if goed == 4:
        reply_text = 'Gewonnen! %s' % emoji.emojize(':muscle:', use_aliases=True)
      else:
        reply_text = 'Helaas, verloren. %s' % emoji.emojize(':sob:', use_aliases=True)
      update.message.reply_text(reply_text,
                                reply_markup=ReplyKeyboardRemove())
      user_data['ronde'] = 1
      return end_game(bot, update, user_data)

def end_game(bot, update, user_data):
    print('in end_game')
    update.message.reply_text('Dat was het!',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
    #TODO show high scores

def cancel(bot, update):
    print('in cancel')
    user = update.message.from_user
    print("User %s canceled the conversation." % user.first_name)
    update.message.reply_text('Tot ziens.',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def error(bot, update, error):
  print('received: %s' % update.message.text)
  print('error: %s' % error)
 
if __name__ == '__main__':
  updater = Updater(API_KEY)
  hearts = "|".join(code_options())

  updater.dispatcher.add_handler(CommandHandler('start', start))
  conv_handler = ConversationHandler(
      entry_points=[CommandHandler('begin', begin)],
      states={
          BEURT: [RegexHandler('^(Ok|Nee|%s)$' % hearts, check_round, pass_user_data=True)]
      },
      fallbacks=[CommandHandler('stoppen', cancel)]
  )
  updater.dispatcher.add_handler(conv_handler)

  updater.dispatcher.add_handler(MessageHandler(Filters.text, logmessage, pass_job_queue=True, pass_chat_data=True))

  updater.dispatcher.add_error_handler(error)

  updater.start_polling()
  updater.idle()

