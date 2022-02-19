from unicodedata import category
import srcomapi, srcomapi.datatypes as dt
from discord.ext.commands import errors
import datetime

def sort_embeddings(embeddings, nb_categories):
    for i in range(nb_categories):
        temp_value = embeddings.pop(nb_categories+i)
        embeddings.insert(2*i+1,temp_value)

    for i in range(nb_categories):
        temp_value = embeddings.pop(nb_categories*2+i)
        embeddings.insert(3*i+2,temp_value)

def get_PBs(runner):
    try:
        runner_id =  api.get("users?lookup={}".format(runner))[0]['id']
    except IndexError:
        raise errors.UserInputError("I haven't found this runner :pensive:\n"
                                    "Make sure you haven't mispelled their SRC username."
                                    )
        
    raw_PBs = api.get("users/{}/personal-bests?embed=category".format(runner_id))
    runner_PBs = {}
    for pb in raw_PBs:
        game_is_main_dead_cells = pb['run']['game'] == 'nd2ee5ed'
        game_is_extension_dead_cells = pb['run']['game'] == 'pdvzlp96'
        game_is_not_dead_cells = not game_is_main_dead_cells and not game_is_extension_dead_cells  
        
        if game_is_not_dead_cells:
            continue 
        
        category = dt.Category(api, data=pb['category']['data']).name
        misc_category = category in ["4BC (obsolete)","Any% (Early Access)", "Fresh File (Early Access)", "Any% Seeded (obsolete)"]
        
        seeded = False
        if game_is_main_dead_cells:
            
            if category == "Fresh File":
                patch_is_21_and_higher = pb['run']['values']['6njzm5pl'] == 'mln9x50q'
                category += " (2.1+)" if patch_is_21_and_higher else " (<2.1)"
            
            elif category == "5BC":
                patch_is_23_and_higher = pb['run']['values']['ylp7pkrl'] == 'p12p7j4q'
                category += " (2.3+)" if patch_is_23_and_higher else " (<2.3)"
            
            seeded = pb['run']['values']['e8m661ql'] == 'p12j3x4q'
        
        if not game_is_main_dead_cells and len(pb['run']['values']) > 0:
            seeded = pb['run']['values']['yn2wwp2n'] == 'klrknyo1'
        
        if seeded and not misc_category:
            runner_PBs[category + " (Seeded)"] = pb
        elif not seeded and not misc_category:
            runner_PBs[category] = pb
    
    return runner_PBs

def get_new_runs():
    newest_run = api.search(srcomapi.datatypes.Run, {"status":"verified","game":"nd2ee5ed","orderby":"verify-date","direction":"desc"})[0]
    print(newest_run) #you get the embed values of the run object by printing it somehow, probably related to cache idk

    category = newest_run.category.name
    seeded = newest_run.values['e8m661ql'] == 'p12j3x4q'
    
    if category == "Fresh File":
        patch_is_21_and_higher = newest_run.values['6njzm5pl'] == 'mln9x50q'
        category += " (2.1+)" if patch_is_21_and_higher else " (<2.1)"
    elif category == "5BC":
        patch_is_23_and_higher = newest_run.values['ylp7pkrl'] == 'p12p7j4q'
        category += " (2.3+)" if patch_is_23_and_higher else " (<2.3)"

    result = {
        "Runner": newest_run.players[0].name,
        "Category": category + " (Seeded)" if seeded else category,
        "Time": str(datetime.timedelta(seconds=newest_run.times["primary_t"])).rstrip('000'),
        "Video Link": newest_run.videos["links"][0]['uri']
    }
    return result

api = srcomapi.SpeedrunCom()
api.debug = 1
