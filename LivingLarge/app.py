from flask import Flask, render_template, request, abort, session, redirect, url_for
from homes import homes 
import random 

app = Flask(__name__)
app.secret_key = "living_large_secret_key"


def default_profile():
   return {
       "city": "",
       "budget": None,
       "min_size": None,
       "rooms": None,
       "wants_shopping": False,
       "wants_garage": False,
       "wants_garden": False,
       "wants_forest": False,
       "wants_commute": False,
       "wants_family": False,
       "wants_investment": False,
   }

def parse_dream_home(text):
   text = text.lower()
   profile = default_profile()
   profile = {
       "city": "",
       "budget": None,
       "min_size": None,
       "rooms": None,
       "wants_shopping": False,
       "wants_garage": False,
       "wants_garden": False,
       "wants_forest": False,
       "wants_commute": False,
       "wants_family": False,
       "wants_investment": False,
   }
   # By
   if "vejle" in text:
       profile["city"] = "Vejle"
   elif "horsens" in text:
       profile["city"] = "Horsens"
   elif "aarhus" in text:
       profile["city"] = "Aarhus"
   elif "randers" in text:
       profile["city"] = "Randers"
   elif "silkeborg" in text:
       profile["city"] = "Silkeborg"
   elif "odense" in text:
       profile["city"] = "Odense"
   elif "københavn" in text:
       profile["city"] = "København"
   elif "esbjerg" in text:
       profile["city"] = "Esbjerg"
   elif "kolding" in text:
       profile["city"] = "Kolding"
   elif "aalborg" in text:
       profile["city"] = "Aalborg"
   elif "blåvand" in text:
       profile["city"] = "Blåvand"
   elif "skagen" in text:
       profile["city"] = "Skagen"
   # Budget
   if "3 mio" in text or "3000000" in text:
       profile["budget"] = 3000000
   if "2 mio" in text or "2000000" in text:
       profile["budget"] = 2000000
   if "4 mio" in text or "4000000" in text:
       profile["budget"] = 4000000
   # Størrelse
   if "stor" in text or "150" in text:
       profile["min_size"] = 150
   # Features
   if "3 værelser" in text or "3 vaerelser" in text:
       profile["rooms"] = 3
   elif "4 værelser" in text or "4 vaerelser" in text:
       profile["rooms"] = 4
   elif "5 værelser" in text or "5 vaerelser" in text:
       profile["rooms"] = 5
   if "garage" in text:
       profile["wants_garage"] = True
   if "have" in text:
       profile["wants_garden"] = True
   if "natur" in text or "skov" in text or "roligt" in text:
       profile["wants_forest"] = True
   if "pendling" in text or "motorvej" in text or "arbejde" in text:
       profile["wants_commute"] = True
   if "familie" in text or "børn" in text or "skole" in text:
       profile["wants_family"] = True
   if "investering" in text:
       profile["wants_investment"] = True
   if "indkøb" in text or "butik" in text or "supermarked" in text:
       profile["wants_shopping"] = True
   return profile

def format_price(price):
   return f"{price:,.0f}".replace(",", ".")
app.jinja_env.globals.update(format_price=format_price)

def calculate_match(user_profile: dict, home: dict) -> int:
   score = 0
   max_score = 0
   if user_profile["city"]:
       max_score += 30
       if home["city"].lower() == user_profile["city"].lower():
           score += 30
   if user_profile["budget"] is not None:
       max_score += 20
       if home["price"] <= user_profile["budget"]:
           score += 20
       elif home["price"] <= user_profile["budget"] * 1.1:
           score += 12
       elif home["price"] <= user_profile["budget"] * 1.2:
           score += 6
   if user_profile["min_size"] is not None:
       max_score += 15
       if home["size"] >= user_profile["min_size"]:
           score += 15
       elif home["size"] >= user_profile["min_size"] * 0.9:
           score += 8
   if user_profile.get("rooms") is not None:
       max_score += 15
       if home.get("rooms", 0) >= user_profile["rooms"]:
           score += 15
       elif home.get("rooms", 0) == user_profile["rooms"] - 1:
           score += 8
   if user_profile.get("wants_shopping", False):
       max_score += 8
       if home.get("near_shopping"):
           score += 8
   if user_profile["wants_garage"]:
       max_score += 8
       if home["garage"]:
           score += 8
   if user_profile["wants_garden"]:
       max_score += 8
       if home["garden"]:
           score += 8
   if user_profile["wants_forest"]:
       max_score += 8
       if home["forest_nearby"]:
           score += 8
   if user_profile["wants_commute"]:
       max_score += 7
       if home["commute_score"] >= 7:
           score += 7
   if user_profile["wants_family"]:
       max_score += 6
       if home["family_score"] >= 7:
           score += 6
   if user_profile["wants_investment"]:
       max_score += 5
       if home["investment_score"] >= 7:
           score += 5
   if max_score == 0:
       return 0
   final_score = round((score / max_score) * 100)
   if final_score < 8:
       final_score = 8
   if final_score > 95:
       final_score = 95
   return final_score

def get_match_reasons(user_profile: dict, home: dict) -> list:
   reasons = []
   if user_profile["city"] and home["city"].lower() == user_profile["city"].lower():
       reasons.append("Rigtig by")
   if user_profile["budget"] is not None:
       if home["price"] <= user_profile["budget"]:
           reasons.append("Inden for budget")
       elif home["price"] <= user_profile["budget"] * 1.1:
           reasons.append("Tæt på budget")
   if user_profile["min_size"] is not None:
       if home["size"] >= user_profile["min_size"]:
           reasons.append("Stor nok")
       elif home["size"] >= user_profile["min_size"] * 0.9:
           reasons.append("Næsten stor nok")
   if user_profile.get("rooms") is not None:
       if home.get("rooms", 0) >= user_profile["rooms"]:
           reasons.append("Nok værelser")        
   if user_profile["wants_garage"] and home["garage"]:
       reasons.append("Garage")
   if user_profile["wants_garden"] and home["garden"]:
       reasons.append("Have")
   if user_profile["wants_forest"] and home["forest_nearby"]:
       reasons.append("Tæt på natur")
   if user_profile["wants_commute"] and home["commute_score"] >= 7:
       reasons.append("Kort pendling")
   if user_profile["wants_family"] and home["family_score"] >= 7:
       reasons.append("Familievenligt")
   if user_profile["wants_investment"] and home["investment_score"] >= 7:
       reasons.append("God investering")
   if user_profile.get("wants_shopping", False) and home.get("near_shopping"):
       reasons.append("Tæt på indkøb")
   return reasons

def get_match_summary(user_profile, home):
   positives = []
   negatives = []
   # POSITIVE MATCHES
   if user_profile["city"] and home["city"].lower() == user_profile["city"].lower():
       positives.append("ligger i din ønskede by")
   if user_profile["budget"] is not None:
       if home["price"] <= user_profile["budget"]:
           positives.append("holder sig inden for budget")
       elif home["price"] > user_profile["budget"] * 1.1:
           negatives.append("ligger over budget")
   if user_profile["min_size"] is not None:
       if home["size"] >= user_profile["min_size"]:
           positives.append("har den ønskede størrelse")
       else:
           negatives.append("er mindre end ønsket")
   if user_profile.get("rooms") is not None:
       if home.get("rooms", 0) >= user_profile["rooms"]:
           positives.append("har nok værelser")        
   if user_profile["wants_garden"] and home["garden"]:
       positives.append("har en have")
   if user_profile["wants_garage"] and home["garage"]:
       positives.append("har garage")
   if user_profile["wants_forest"] and home["forest_nearby"]:
       positives.append("ligger tæt på naturen")
   if user_profile["wants_commute"] and home["commute_score"] >= 7:
       positives.append("har god pendlerafstand")
   if user_profile.get("wants_shopping", False) and home.get("near_shopping"):
       positives.append("er tæt på indkøb")
   # GENERÉR TEKST
   if positives:
           text = "Boligen matcher godt dine ønsker, fordi den " + " og ".join(positives[:2])
   else:
       text = "Boligen matcher delvist dine ønsker"
   if negatives:
       text += ", men " + ", ".join(negatives[:1])
   return text + "."

def get_match_improvement(user_profile, home):
   issues = []
   if user_profile["budget"] is not None and home["price"] > user_profile["budget"]:
       issues.append("prisen ligger over dit budget")
   if user_profile["min_size"] is not None and home["size"] < user_profile["min_size"]:
       issues.append("boligen er mindre end ønsket")
   if user_profile["wants_commute"] and home["commute_score"] < 7:
       issues.append("pendlingen er lidt længere")
   if not issues:
       return ""
   return "Matchen er lavere fordi " + ", ".join(issues) + "."

def get_lifestyle_comment(home):
   comments = []
   if home["family_score"] >= 8:
       comments.append("Området er meget familievenligt")
   if home["commute_score"] >= 8:
       comments.append("Pendlingen er kort")
   if home["investment_score"] >= 8:
       comments.append("Boligen har stærkt investeringspotentiale")
   if not comments:
       return ""
   return "Fremtidsperspektiv: " + ", ".join(comments) + "."

def get_match_limitations(user_profile, home):
   reasons = []
   if user_profile["budget"] is not None and home["price"] > user_profile["budget"]:
       reasons.append("Boligen ligger over dit budget")
   if user_profile["min_size"] is not None and home["size"] < user_profile["min_size"]:
       reasons.append("Boligen er mindre end ønsket")
   if user_profile["wants_garage"] and not home["garage"]:
       reasons.append("Boligen har ikke garage")
   if user_profile["wants_garden"] and not home["garden"]:
       reasons.append("Boligen har ikke have")
   if user_profile["wants_forest"] and not home["forest_nearby"]:
       reasons.append("Boligen ligger ikke tæt på skov")
   if user_profile.get("wants_shopping", False) and not home.get("near_shopping"):
       reasons.append("Boligen ligger ikke tæt på indkøb")
   return reasons

def get_match_count(user_profile: dict, home: dict):
   total = 0
   matched = 0
   if user_profile["city"]:
       total += 1
       if home["city"].lower() == user_profile["city"].lower():
           matched += 1
   if user_profile["budget"] is not None:
       total += 1
       if home["price"] <= user_profile["budget"]:
           matched += 1
   if user_profile["min_size"] is not None:
       total += 1
       if home["size"] >= user_profile["min_size"]:
           matched += 1
   if user_profile["wants_garage"]:
       total += 1
       if home["garage"]:
           matched += 1
   if user_profile["wants_garden"]:
       total += 1
       if home["garden"]:
           matched += 1
   if user_profile["wants_forest"]:
       total += 1
       if home["forest_nearby"]:
           matched += 1
   if user_profile["wants_commute"]:
       total += 1
       if home["commute_score"] >= 7:
           matched += 1
   if user_profile["wants_family"]:
       total += 1
       if home["family_score"] >= 7:
           matched += 1
   if user_profile["wants_investment"]:
       total += 1
       if home["investment_score"] >= 7:
           matched += 1
   if user_profile.get("wants_shopping", False):
       total += 1
       if home.get("near_shopping"):
           matched += 1
   return matched, total

def get_lifestyle_tags(home):
   tags = []
   if home.get("family_score", 0) >= 7:
       tags.append("Perfekt til familie")
   if home.get("forest_nearby"):
       tags.append("Tæt på natur")
   if home.get("commute_score", 0) >= 7:
       tags.append("Kort pendling")
   if home.get("investment_score", 0) >= 7:
       tags.append("God investering")
   return tags

def get_top_matches_explanation(user_profile, matches):
   if not matches:
       return ""
   # Tag top 3
   top_matches = matches[:3]
   reasons = []
   for match in top_matches:
       home = match
       if user_profile["budget"] is not None:
           if home["price"] <= user_profile["budget"]:
               reasons.append("inden for budget")
           else:
               reasons.append("over budget")
       if user_profile["min_size"] is not None:
           if home["size"] >= user_profile["min_size"]:
               reasons.append("stor nok")
           else:
               reasons.append("for lille")
       if user_profile["wants_garden"] and home.get("garden"):
           reasons.append("have")
       if user_profile["wants_garage"] and home.get("garage"):
           reasons.append("garage")
       if user_profile["wants_forest"] and home.get("forest_nearby"):
           reasons.append("tæt på natur")
       if user_profile.get("wants_shopping", False) and home.get("near_shopping"):
           reasons.append("tæt på indkøb")
   # Fjern duplicates
   unique_reasons = []
   for r in reasons:
       if r not in unique_reasons:
           unique_reasons.append(r)
   # Tag maks 3
   top_reasons = unique_reasons[:3]
   if not top_reasons:
    return "Vi har udvalgt disse boliger ud fra din samlede profil."
   if len(top_reasons) == 1:
    reason_text = top_reasons[0]
   elif len(top_reasons) == 2:
    reason_text = " og ".join(top_reasons)
   else:
    reason_text = ", ".join(top_reasons[:-1]) + " og " + top_reasons[-1]
   return "Vi har udvalgt disse boliger, fordi de matcher dine vigtigste ønsker – især " + reason_text + "."

def get_matches(user_profile: dict, homes_list: list) -> list:
   matches = []
   low_matches = []
   minimum_match_score = 25
   used_fallback = False
   shuffled_homes = homes_list[:]
   random.shuffle(shuffled_homes)
   for home in shuffled_homes:
       match_score = calculate_match(user_profile, home)
       home_with_score = home.copy()
       home_with_score["match_score"] = match_score
       if match_score < minimum_match_score:
           low_matches.append(home_with_score)
           continue
       if match_score >= 75:
           match_label = "Perfekt match"
       elif match_score >= 55:
           match_label = "Godt match"
       elif match_score >= 35:
           match_label = "Okay match"
       else:
           match_label = "Svagt match"
       home_with_score["match_label"] = match_label
       match_details = []
       if home["city"].lower() == user_profile["city"].lower():
           match_details.append("✓ Rigtig by")
       else:
           match_details.append("✗ Forkert by")
       if user_profile["budget"] is not None:
           if home["price"] <= user_profile["budget"]:
               match_details.append("✓ Inden for budget")
           else:
               match_details.append("✗ Over budget")
       if user_profile["min_size"] is not None:
           if home["size"] >= user_profile["min_size"]:
               match_details.append("✓ Stor nok")
           else:
               match_details.append("✗ For lille")
       if user_profile["wants_garage"]:
           match_details.append("✓ Garage" if home["garage"] else "✕ Ingen garage")
       if user_profile["wants_family"]:
           match_details.append(
               "✓ Familievenligt område"
               if home["family_score"] >= 7
               else "✕ Ikke familievenligt"
           )
       if user_profile["wants_forest"]:
           match_details.append(
               "✓ Tæt på natur"
               if home["forest_nearby"]
               else "✕ Ikke tæt på natur"
           )
       if user_profile["wants_investment"]:
           match_details.append(
               "✓ God investering"
               if home["investment_score"] >= 7
               else "✕ Svag investering"
           )
       if user_profile.get("wants_shopping", False):
           match_details.append(
                "✓ Tæt på indkøb" if home.get("near_shopping") else "✗ Ikke tæt på indkøb"
           )
       home_with_score["match_reasons"] = get_match_reasons(user_profile, home)
       home_with_score["match_summary"] = get_match_summary(user_profile, home)
       home_with_score["limitations"] = get_match_limitations(user_profile, home)
       home_with_score["match_improvement"] = get_match_improvement(user_profile, home)
       home_with_score["future_comment"] = get_lifestyle_comment(home)
       home_with_score["tags"] = get_lifestyle_tags(home)
       matched_count, total_count = get_match_count(user_profile, home)
       home_with_score["match_details"] = match_details
       home_with_score["matched_count"] = matched_count
       home_with_score["total_count"] = total_count
       # Tie-break data:
       # 1. hvor mange ting matcher
       # 2. lille random jitter så næsten ens boliger varierer
       home_with_score["_tie_strength"] = matched_count
       home_with_score["_tie_random"] = random.uniform(0, 0.35)
       matches.append(home_with_score)
   # Sortér først efter rigtig matchscore, derefter hvor mange ting der matcher,
   # og til sidst en meget lille random variation for at sikre variation i næsten ens boliger
   matches.sort(
       key=lambda x: (
           x["match_score"],
           x["_tie_strength"],
           x["_tie_random"],
       ),
       reverse=True,
   )
   if not matches:
       matches = sorted(low_matches, key=lambda x: x["match_score"], reverse=True)[:5]
       used_fallback = True

   return matches, used_fallback

@app.route("/", methods=["GET", "POST"])
def home():
   results = []
   explanation = ""
   no_results_message = ""
   used_fallback = False
   user = session.get("user_profile", default_profile())
   dream_text = session.get("last_dream_home", "")
   if request.method == "POST":
       dream_text = request.form.get("dream_home", "").strip()
       if dream_text:
           user = parse_dream_home(dream_text)
       else:
           user = default_profile()
           user["city"] = request.form.get("city", "").strip()
           user["budget"] = int(request.form.get("budget")) if request.form.get("budget") else None
           user["min_size"] = int(request.form.get("min_size")) if request.form.get("min_size") else None
           user["rooms"] = int(request.form.get("rooms")) if request.form.get("rooms") else None
           user["wants_shopping"] = "wants_shopping" in request.form
           user["wants_garage"] = "wants_garage" in request.form
           user["wants_garden"] = "wants_garden" in request.form
           user["wants_forest"] = "wants_forest" in request.form
           user["wants_commute"] = "wants_commute" in request.form
           user["wants_family"] = "wants_family" in request.form
           user["wants_investment"] = "wants_investment" in request.form
       session["user_profile"] = user
       session["last_dream_home"] = dream_text
       return redirect(url_for("home", _anchor="results-section"))
   if user:
       results, used_fallback = get_matches(user, homes)
       if user and not results:
           no_results_message = "Vi fandt desværre ingen boliger, der matcher præcist. Prøv at hæv dit budget lidt, vælg et andet område, eller juster på dine krav."
       explanation = get_top_matches_explanation(user, results)
   return render_template(
       "index.html",
       results=results,
       favorites=session.get("favorites", []),
       user=user,
       homes=homes,
       explanation=explanation,
       no_results_message=no_results_message,
       used_fallback=used_fallback,
       dream_text=dream_text,
   )


@app.route("/bolig/<int:home_id>")
def bolig_detaljer(home_id):
   if home_id < 0 or home_id >= len(homes):
       abort(404)
   home = homes[home_id]
   user_profile = session.get("user_profile")
   if user_profile:
       match_score = calculate_match(user_profile, home)
       match_reasons = get_match_reasons(user_profile, home)
       match_summary = get_match_summary(user_profile, home)
   else:
       match_score = 0
       match_reasons = []
       match_summary = "Vælg dine kriterier på forsiden for at se hvorfor boligen matcher."
   return render_template(
       "details.html",
       home=home,
       match_score=match_score,
       match_reasons=match_reasons,
       match_summary=match_summary,
       user_profile=user_profile
   )    
@app.route("/toggle_favorite/<int:home_id>")
def toggle_favorite(home_id):
   if "favorites" not in session:
       session["favorites"] = []
   favorites = session["favorites"]
   if home_id in favorites:
       favorites.remove(home_id)
   else:
       favorites.append(home_id)
   session["favorites"] = favorites
   return redirect(request.referrer or "/")

@app.route("/profile", methods=["GET", "POST"])
def profile():
   if not session.get("logged_in"):
       return redirect(url_for("login"))
   user_profile = session.get("user_profile", default_profile())
   if request.method == "POST":
       user_profile["city"] = request.form.get("city", "").strip()
       user_profile["budget"] = int(request.form.get("budget")) if request.form.get("budget") else None
       user_profile["min_size"] = int(request.form.get("min_size")) if request.form.get("min_size") else None
       user_profile["rooms"] = int(request.form.get("rooms")) if request.form.get("rooms") else None
       selected_preferences = request.form.getlist("preferences")
       user_profile["wants_garden"] = "garden" in selected_preferences
       user_profile["wants_garage"] = "garage" in selected_preferences
       user_profile["wants_forest"] = "forest" in selected_preferences
       user_profile["wants_shopping"] = "shopping" in selected_preferences
       user_profile["wants_commute"] = "commute" in selected_preferences
       user_profile["wants_family"] = "family" in selected_preferences
       user_profile["wants_investment"] = "investment" in selected_preferences
       session["user_profile"] = user_profile
       return redirect(url_for("profile"))
   favorite_ids = session.get("favorites", [])
   favorite_homes = [home for home in homes if home["id"] in favorite_ids]
   return render_template(
       "profile.html",
       user_profile=user_profile,
       favorite_homes=favorite_homes
   )

@app.route("/login", methods=["GET", "POST"])
def login():
   if request.method == "POST":
       email = request.form.get("email", "").strip()
       password = request.form.get("password", "").strip()
       # MVP placeholder
       session["logged_in"] = True
       session["user_email"] = email
       return redirect(url_for("profile"))
   return render_template("login.html")

@app.route("/about")
def about():
   return render_template("about.html")

@app.route("/reset")
def reset():
   session.clear()
   return redirect(url_for("home") + "#top")

if __name__ == "__main__":
   app.run(host="0.0.0.0", port=10000)
