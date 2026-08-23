import os
import re

directory = '.'

button_html = '            <button class="mobile-menu-toggle"><i class="ph-bold ph-list"></i></button>\n        </div>\n    </header>'
script_html = '''
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const menuToggle = document.querySelector('.mobile-menu-toggle');
            const navLinks = document.querySelector('.nav-links');
            if (menuToggle && navLinks) {
                menuToggle.addEventListener('click', function() {
                    navLinks.classList.toggle('active');
                });
            }
        });
    </script>
</body>
'''

for filename in os.listdir(directory):
    if filename.endswith('.html'):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already added
        if 'mobile-menu-toggle' not in content:
            # Replace </div>\s*</header> with button
            content = re.sub(r'</div>\s*</header>', button_html, content, count=1)
            
            # Replace </body> with script
            content = re.sub(r'</body>', script_html, content, count=1)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated {filename}")
        else:
            print(f"Skipped {filename} (already has toggle)")
