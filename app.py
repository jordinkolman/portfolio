import os
from flask import Flask, render_template, jsonify, abort
import json
import markdown
import glob
import mammoth

app = Flask(__name__)

# Basic Markdown parser setup
def get_blog_posts():
    posts = []
    blog_dir = 'blog'
    if not os.path.exists(blog_dir):
        return posts
        
    for filepath in glob.glob(os.path.join(blog_dir, '*.md')):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Convert markdown to html
            md = markdown.Markdown(extensions=['meta'])
            html_content = md.convert(content)
            
            # Extract meta if present, otherwise set defaults
            filename = os.path.basename(filepath)
            slug = os.path.splitext(filename)[0]
            
            meta = getattr(md, 'Meta', {})
            title = meta.get('title', [slug.replace('-', ' ').title()])[0]
            date = meta.get('date', [''])[0]
            summary = meta.get('summary', [''])[0]
            
            posts.append({
                'slug': slug,
                'title': title,
                'date': date,
                'summary': summary,
                'content': html_content
            })
            
    # Sort posts by date descending (assuming YYYY-MM-DD or similar sortable date)
    posts.sort(key=lambda x: x['date'], reverse=True)
    return posts

def get_projects():
    projects_path = 'data/projects.json'
    if os.path.exists(projects_path):
        with open(projects_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

@app.route('/')
def home():
    # Fetch recent blog posts for homepage
    recent_posts = get_blog_posts()[:3]
    return render_template('index.html', recent_posts=recent_posts)

@app.route('/resume')
def resume():
    resume_path = os.path.join('static', 'assets', 'SWEResume2026.docx')
    resume_html = ""
    try:
        # Custom style mapping to control how Word styles become HTML elements
        style_map = """
        p[style-name='Title'] => h1:fresh
        p[style-name='Subtitle'] => h2:fresh
        """
        with open(resume_path, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file, style_map=style_map)
            # Remove any trailing headings or bizarrely mapped elements causing the 'Skills' issue
            # Sometimes mammoth defaults lists to plain paragraphs if not mapped, which is standard.
            resume_html = result.value
    except Exception as e:
        resume_html = "<p>Error loading resume content.</p>"
        
    return render_template('resume.html', resume_content=resume_html)

@app.route('/projects')
def projects():
    return render_template('projects.html', projects=get_projects())

@app.route('/blog')
def blog():
    return render_template('blog.html', posts=get_blog_posts())

@app.route('/blog/<slug>')
def post(slug):
    posts = get_blog_posts()
    post_data = next((p for p in posts if p['slug'] == slug), None)
    if not post_data:
        abort(404)
    return render_template('post.html', post=post_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
