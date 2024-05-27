from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key


# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        first = request.form['first']
        last = request.form['last']
        contact = request.form['contact']
        users = load_users()
        if username in users:
            flash("Username already exists!")
            return redirect(url_for('signup'))
        users[username] = password
        try:
            save_users(users)
            flash("Signup successful! Please log in.")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Error saving user data: {str(e)}")
            return redirect(url_for('signup'))
    return render_template('signup.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        if username not in users or users[username] != password:
            flash("Invalid username or password!")
            return redirect(url_for('login'))
        session['username'] = username
        return redirect(url_for('index'))
    return render_template('login.html')

# Index route
def load_users():
    try:
        if not os.path.exists('users.json'):
            return {}
        with open('users.json', 'r') as file:
            users = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        users = {}
    return users

# Function to save user data to JSON file
def save_users(users):
    with open('users.json', 'w') as file:
        json.dump(users, file, indent=4)

# Function to load property data from JSON file
def load_properties():
    try:
        if not os.path.exists('properties.json'):
            return []
        with open('properties.json', 'r') as file:
            properties = json.load(file)
            # Ensure 'likes' attribute exists for each property
            for property in properties:
                if 'likes' not in property:
                    property['likes'] = 0
    except (FileNotFoundError, json.JSONDecodeError):
        properties = []
    return properties

# Function to save property data to JSON file
def save_properties(properties):
    with open('properties.json', 'w') as file:
        json.dump(properties, file, indent=4)

@app.route('/')
def index():
    if 'username' in session:
        page = request.args.get('page', 1, type=int)
        location = request.args.get('location', type=str)
        min_price = request.args.get('min_price', type=str)
        max_price = request.args.get('max_price', type=str)
        min_beds = request.args.get('min_beds', type=str)
        max_beds = request.args.get('max_beds', type=str)

        properties = load_properties()

        # Apply filters
        filtered_properties = []
        for prop in properties:
            if location and location.lower() not in prop['location'].lower():
                continue
            if min_price is not None:
                try:
                    if int(prop['price']) < int(min_price):
                        continue
                except ValueError:
                    pass
            if max_price is not None:
                try:
                    if int(prop['price']) > int(max_price):
                        continue
                except ValueError:
                    pass
            if min_beds is not None:
                try:
                    if int(prop['beds']) < int(min_beds):
                        continue
                except ValueError:
                    pass
            if max_beds is not None:
                try:
                    if int(prop['beds']) > int(max_beds):
                        continue
                except ValueError:
                    pass
            filtered_properties.append(prop)

        properties = filtered_properties

        per_page = 10  # Number of properties per page
        start = (page - 1) * per_page
        end = start + per_page
        paginated_properties = properties[start:end]

        return render_template('index.html', properties=paginated_properties, username=session['username'], 
                               location=location, min_price=min_price, max_price=max_price, min_beds=min_beds, max_beds=max_beds)
    return redirect(url_for('login'))
    return redirect(url_for('login'))





# Sell route
@app.route('/sell', methods=['GET', 'POST'])
def sell():
    if 'username' in session:
        if request.method == 'POST':
            name = request.form['name']
            location = request.form['location']
            area = request.form['area']
            price = request.form['price']
            age = request.form['age']
            beds = request.form['beds']
            baths = request.form['baths']
            email = request.form['email']
            contact = request.form['contact']

            property_data = {
                'name': name,
                'location': location,
                'area': area,
                'price': price,
                'age': age,
                'email': email,
                'contact': contact,
                'beds': beds,
                'baths': baths,
                'likes': 0
            }

            properties = load_properties()
            properties.append(property_data)
            save_properties(properties)

            return redirect(url_for('index'))
        return render_template('sell.html')
    return redirect(url_for('login'))

@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit(index):
    properties = load_properties()
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        area = request.form['area']
        price = request.form['price']
        age = request.form['age']
        beds = request.form['beds']
        baths = request.form['baths']
        email = request.form['email']
        contact = request.form['contact']
        if index < len(properties):
            properties[index] = {
                'name': name,
                'location': location,
                'area': area,
                'price': price,
                'age': age,
                'email': email,
                'contact': contact,
                'beds': beds,
                'baths': baths,
                'likes': properties[index]['likes']  # Keep likes count unchanged
            }
            save_properties(properties)
            return redirect(url_for('index'))
    elif index < len(properties):
        property_to_edit = properties[index]
        return render_template('edit.html', property_index=index, property=property_to_edit)  # Pass index as property_index
    return redirect(url_for('index'))

@app.route('/delete/<int:index>', methods=['POST'])
def delete(index):
    properties = load_properties()
    if index < len(properties):
        del properties[index]
        save_properties(properties)
    return redirect(url_for('index'))

@app.route('/like/<int:index>', methods=['POST'])
def like(index):
    properties = load_properties()
    if index < len(properties):
        properties[index]['likes'] += 1
        save_properties(properties)
    return redirect(url_for('index'))

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    
    app.run(debug=True)
