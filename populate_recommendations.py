import MySQLdb
from itertools import product

# Database connection
db = MySQLdb.connect(
    host="localhost",
    user="root",
    password="Messipratham30",
    database="clothing_recommendations"
)
cursor = db.cursor()

# All possible combinations
genders = ['Male', 'Female', 'Unisex']
hair_types = ['Short', 'Medium', 'Long']
face_shapes = ['Oval', 'Round', 'Square']
body_shapes = ['Rectangular', 'Pear-Shaped', 'Inverted Triangle']

# Sample products data structure
products = {
    'Male': {
        'Oval': {
            'Short': {
                'Rectangular': ['Classic Fit Blazer', 'Tailored Dress Shirt'],
                'Pear-Shaped': ['Slim Fit Dress Shirt', 'Vertical Striped Shirt'],
                'Inverted Triangle': ['Single-Breasted Coat', 'Structured Blazer']
            },
            # More combinations...
        }
    },
    'Female': {
        'Oval': {
            'Long': {
                'Inverted Triangle': ['V-Neck Maxi Dress', 'Wrap Style Blouse'],
                # More combinations...
            }
        }
    },
    'Unisex': {
        'Oval': {
            'Medium': {
                'Rectangular': ['Classic Denim Jacket', 'Neutral Tone Sweater'],
                # More combinations...
            }
        }
    }
}

def generate_recommendations():
    for gender, face, hair, body in product(genders, face_shapes, hair_types, body_shapes):
        # Skip impossible combinations (e.g., long hair for some styles)
        if gender == 'Male' and hair == 'Long' and body == 'Inverted Triangle':
            continue
            
        items = products.get(gender, {}).get(face, {}).get(hair, {}).get(body, [])
        
        for item_name in items:
            # Generate realistic product details
            price = round(39.99 + (hash(item_name) % 6000)/100, 2)  # Random price $39.99-$99.99
            size = 'XS,S,M,L,XL' if gender == 'Unisex' else 'S,M,L,XL'
            material = 'Cotton' if price < 60 else 'Wool' if price < 80 else 'Silk'
            image = f"{gender[0].lower()}_{face[:3].lower()}_{hair[:3].lower()}_{body[:3].lower()}.jpg"
            
            # Insert into database
            cursor.execute("""
                INSERT INTO recommended_clothes 
                (name, price, image, size, material, gender, hair_type, face_shape, body_shape)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (item_name, price, image, size, material, gender, hair, face, body))
    
    db.commit()
    print("Database populated successfully!")

if __name__ == "__main__":
    generate_recommendations()
    db.close()