import os

from db_handler import get_user_email
from flat_finder import scrape_new_flats_for_user
from mail_handler import sent_flat_info_list

# logging.basicConfig(format='%(asctime)s : %(levelname)s  :  %(message)s',
# filename='/home/teasko/Projects/Flat_Crawler/src/mainlog.log', level=logging.INFO)

if __name__ == "__main__":
    user_id = os.getenv("user_id")
    new_flats = scrape_new_flats_for_user(user_id)
    user_email = get_user_email(user_id=user_id)
    sent_flat_info_list(new_flats, user_email)
