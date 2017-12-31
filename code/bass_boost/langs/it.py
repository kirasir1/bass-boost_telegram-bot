from .en import Lang as LBase

class Lang(LBase):
    """ Thanks @danogentili """
    lang = "it"
    format_unsupported = "Formato audio non supportato."
    start_message = "Questo bot può potenziare i bassi di file audio mandati ad esso. Mandami una canzone."
    help_message = start_message + "\n\nQuesto bot fa parte del network di bot @luckydonaldsbots.\n\nQUESTO BOT FA SCHIFO\nEHI!!! BELLOH!!! PERCHÈ LO STAI ANCORA USANDO?!?"
    caption = "@{bot} ha appena potenziato i tuoi bassi!"
    progress1 = "caricamento audio"
    progress0 = "scaricamento file"
    progress2 = "lettura traccia audio"
    progress3 = "calcolo del potenziamento medio necessario"
    progress4 = "calcolo del potenziamento necessario"
    progress5 = "calcolo del potenziamento potenziato necessario"
    progress6 = "estrazione delle regioni da potenziare"
    progress7 = "applicazione dei bassi potenziati alla traccia originale"
    capslock_number_1 = "UNO"
    capslock_number_11 = "UNDICI"
    capslock_number_111 = "CENTOEUNDICI"
    generic_error = "C'è stato un errore. Riprova dopo che è stato corretto."
    task_scheduled = "La tua traccia è stata aggiunta alla coda di potenziamento."