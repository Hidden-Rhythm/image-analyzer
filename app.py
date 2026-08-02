#!/usr/bin/env python3
"""
Image Analyzer - Forensic Image Analysis Tool
Built by Hidden_Rhythm
Deployed on Vercel
"""

import os
import sys
import json
import hashlib
import base64
import tempfile
import shutil
import math
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image, ImageStat

# Try optional imports
try:
    import piexif
    PIEXIF_AVAILABLE = True
except ImportError:
    piexif = None
    PIEXIF_AVAILABLE = False

try:
    import exifread
    EXIFREAD_AVAILABLE = True
except ImportError:
    exifread = None
    EXIFREAD_AVAILABLE = False

try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    cv2 = None
    np = None

try:
    import folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False
    folium = None

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'osint-secret-key-2024')
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# Create upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


class ImageAnalyzer:
    def __init__(self, image_path: str):
        self.image_path = Path(image_path)
        self.image = None
        self.results = {}
        self.load_image()
    
    def load_image(self):
        try:
            self.image = Image.open(self.image_path)
        except Exception as e:
            raise Exception(f"Failed to load image: {e}")
    
    def analyze_basic_info(self):
        if self.image is None:
            return {}
        
        img = self.image
        info = {
            'filename': self.image_path.name,
            'file_size': self.image_path.stat().st_size,
            'file_size_formatted': self._format_size(self.image_path.stat().st_size),
            'format': str(img.format) if img.format else 'Unknown',
            'mode': str(img.mode) if img.mode else 'Unknown',
            'width': img.size[0] if img.size else 0,
            'height': img.size[1] if img.size else 0,
            'aspect_ratio': round(img.size[0] / img.size[1], 2) if img.size and img.size[1] > 0 else 0.0,
            'created': datetime.fromtimestamp(self.image_path.stat().st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(self.image_path.stat().st_mtime).isoformat(),
            'is_animated': getattr(img, 'is_animated', False),
            'n_frames': getattr(img, 'n_frames', 1)
        }
        self.results['basic_info'] = info
        return info
    
    def extract_exif(self):
        if self.image is None:
            return {}
        
        exif_data = {}
        
        if PIEXIF_AVAILABLE and piexif is not None:
            try:
                exif_dict = piexif.load(str(self.image_path))
                if exif_dict:
                    parsed = self._parse_piexif(exif_dict)
                    if parsed:
                        exif_data['piexif'] = parsed
            except Exception:
                pass
        
        if EXIFREAD_AVAILABLE and exifread is not None:
            try:
                with open(self.image_path, 'rb') as f:
                    tags = exifread.process_file(f, details=False)
                    if tags:
                        parsed = self._parse_exifread(tags)
                        if parsed:
                            exif_data['exifread'] = parsed
            except Exception:
                pass
        
        gps = self._extract_gps()
        if gps:
            exif_data['gps'] = gps
            self.results['gps'] = gps
        
        if exif_data:
            self.results['exif'] = exif_data
        return exif_data
    
    def _parse_piexif(self, exif_dict):
        result = {}
        tag_names = {
            '0th': {271: 'Make', 272: 'Model', 305: 'Software', 306: 'DateTime', 315: 'Artist'},
            'Exif': {
                33434: 'ExposureTime', 33437: 'FNumber', 34850: 'ExposureProgram',
                34855: 'ISOSpeedRatings', 36867: 'DateTimeOriginal', 36868: 'DateTimeDigitized',
                37377: 'ShutterSpeedValue', 37378: 'ApertureValue', 37379: 'BrightnessValue',
                37380: 'ExposureBiasValue', 37381: 'MaxApertureValue', 37383: 'MeteringMode',
                37385: 'Flash', 37386: 'FocalLength', 40961: 'ColorSpace',
                40962: 'ExifImageWidth', 40963: 'ExifImageHeight'
            }
        }
        
        for ifd, tags in tag_names.items():
            if ifd in exif_dict:
                for tag_id, tag_name in tags.items():
                    if tag_id in exif_dict[ifd]:
                        value = exif_dict[ifd][tag_id]
                        if isinstance(value, bytes):
                            try:
                                value = value.decode('utf-8', errors='ignore').strip('\x00')
                            except Exception:
                                value = value.hex()
                        elif isinstance(value, tuple) and len(value) == 2 and value[1] != 0:
                            value = round(value[0] / value[1], 2)
                        result[tag_name] = str(value)
        
        return result
    
    def _parse_exifread(self, tags):
        result = {}
        for tag, value in tags.items():
            tag_name = str(tag).replace('Image ', '').replace('EXIF ', '').replace('GPS ', '')
            tag_name = tag_name.replace('Tag ', '')
            val = str(value).replace('EXIF', '').replace('ASCII', '').strip()
            if len(val) > 1 and val not in ['None', '']:
                result[tag_name] = val
        return result
    
    def _extract_gps(self):
        if not PIEXIF_AVAILABLE or piexif is None:
            return None
        
        gps = None
        
        try:
            exif_dict = piexif.load(str(self.image_path))
            if 'GPS' in exif_dict and exif_dict['GPS']:
                gps_data = exif_dict['GPS']
                if gps_data:
                    try:
                        lat_ref_raw = gps_data.get(1, b'N')
                        lat_ref = lat_ref_raw.decode('utf-8', errors='ignore') if isinstance(lat_ref_raw, bytes) else 'N'
                        
                        lat = gps_data.get(2)
                        if lat and isinstance(lat, tuple) and len(lat) == 3:
                            lat_val = (lat[0][0] / lat[0][1] + 
                                      lat[1][0] / lat[1][1] / 60 + 
                                      lat[2][0] / lat[2][1] / 3600)
                            if lat_ref == 'S':
                                lat_val = -lat_val
                            
                            lon_ref_raw = gps_data.get(3, b'E')
                            lon_ref = lon_ref_raw.decode('utf-8', errors='ignore') if isinstance(lon_ref_raw, bytes) else 'E'
                            
                            lon = gps_data.get(4)
                            if lon and isinstance(lon, tuple) and len(lon) == 3:
                                lon_val = (lon[0][0] / lon[0][1] + 
                                          lon[1][0] / lon[1][1] / 60 + 
                                          lon[2][0] / lon[2][1] / 3600)
                                if lon_ref == 'W':
                                    lon_val = -lon_val
                                
                                gps = {
                                    'latitude': round(lat_val, 6),
                                    'longitude': round(lon_val, 6),
                                    'latitude_ref': lat_ref,
                                    'longitude_ref': lon_ref
                                }
                    except Exception:
                        pass
        except Exception:
            pass
        
        return gps
    
    def generate_hashes(self):
        with open(self.image_path, 'rb') as f:
            data = f.read()
        
        hashes = {
            'md5': hashlib.md5(data).hexdigest(),
            'sha1': hashlib.sha1(data).hexdigest(),
            'sha256': hashlib.sha256(data).hexdigest(),
            'sha512': hashlib.sha512(data).hexdigest()
        }
        self.results['hashes'] = hashes
        return hashes
    
    def _safe_get_rgb_values(self, stat_values):
        if stat_values is None:
            return 0.0, 0.0, 0.0
        
        if isinstance(stat_values, tuple):
            if len(stat_values) >= 3:
                return float(stat_values[0]), float(stat_values[1]), float(stat_values[2])
            elif len(stat_values) > 0:
                r = float(stat_values[0]) if len(stat_values) > 0 else 0.0
                g = float(stat_values[1]) if len(stat_values) > 1 else 0.0
                return r, g, 0.0
            return 0.0, 0.0, 0.0
        
        if isinstance(stat_values, list):
            if len(stat_values) >= 3:
                return float(stat_values[0]), float(stat_values[1]), float(stat_values[2])
            elif len(stat_values) > 0:
                r = float(stat_values[0]) if len(stat_values) > 0 else 0.0
                g = float(stat_values[1]) if len(stat_values) > 1 else 0.0
                return r, g, 0.0
            return 0.0, 0.0, 0.0
        
        if isinstance(stat_values, (int, float)):
            val = float(stat_values)
            return val, val, val
        
        try:
            values = list(stat_values)
            if len(values) >= 3:
                return float(values[0]), float(values[1]), float(values[2])
            elif len(values) > 0:
                r = float(values[0]) if len(values) > 0 else 0.0
                g = float(values[1]) if len(values) > 1 else 0.0
                return r, g, 0.0
            return 0.0, 0.0, 0.0
        except (TypeError, ValueError, AttributeError):
            return 0.0, 0.0, 0.0
    
    def analyze_colors(self):
        if self.image is None:
            return {'error': 'No image loaded'}
        
        try:
            img = self.image
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            stat = ImageStat.Stat(img)
            
            mean_r, mean_g, mean_b = self._safe_get_rgb_values(stat.mean)
            std_r, std_g, std_b = self._safe_get_rgb_values(stat.stddev)
            
            gray = self.image.convert('L')
            pixels = list(gray.getdata())
            hist = [0] * 256
            for p in pixels:
                hist[p] += 1
            total = len(pixels)
            entropy = 0.0
            for count in hist:
                if count > 0:
                    p_val = count / total
                    if p_val > 0:
                        entropy -= p_val * math.log2(p_val)
            
            colors = {
                'mean_rgb': {
                    'r': round(mean_r, 2),
                    'g': round(mean_g, 2),
                    'b': round(mean_b, 2)
                },
                'brightness': round((mean_r + mean_g + mean_b) / 3, 2),
                'entropy': round(entropy, 2),
                'std_rgb': {
                    'r': round(std_r, 2),
                    'g': round(std_g, 2),
                    'b': round(std_b, 2)
                }
            }
            
            self.results['colors'] = colors
            return colors
        except Exception as e:
            return {'error': str(e)}
    
    def detect_manipulation(self):
        ela_score = 0.0
        warnings = []
        confidence = 0
        
        if OPENCV_AVAILABLE and cv2 is not None and np is not None and self.image is not None:
            try:
                temp_dir = tempfile.mkdtemp()
                orig_path = os.path.join(temp_dir, 'original.jpg')
                comp_path = os.path.join(temp_dir, 'compressed.jpg')
                
                self.image.save(orig_path, 'JPEG', quality=95)
                self.image.save(comp_path, 'JPEG', quality=75)
                
                orig = cv2.imread(orig_path)
                comp = cv2.imread(comp_path)
                
                if orig is not None and comp is not None:
                    diff = cv2.absdiff(orig, comp)
                    diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
                    diff_float = diff_gray.astype(np.float32)
                    ela_score = float(np.mean(diff_float))
                
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass
        else:
            warnings.append("OpenCV not installed - ELA disabled")
        
        try:
            if 'exif' in self.results:
                exif = self.results['exif']
                if 'piexif' in exif:
                    if 'Software' in exif['piexif']:
                        software = exif['piexif']['Software'].lower()
                        if any(sw in software for sw in ['photoshop', 'gimp', 'paint', 'editor']):
                            warnings.append(f"Editing software: {software}")
                            confidence += 30
            
            if 'colors' in self.results and self.results['colors'].get('entropy', 0) > 7.5:
                entropy_val = self.results['colors']['entropy']
                warnings.append(f"High entropy: {entropy_val:.2f}")
                confidence += 25
            
            if ela_score > 30:
                warnings.append(f"ELA score: {ela_score:.2f}")
                confidence += 30
        except Exception:
            pass
        
        manipulation = {
            'ela_score': round(ela_score, 2),
            'warnings': warnings,
            'confidence': min(confidence, 95),
            'suspect': confidence > 40,
            'opencv_available': OPENCV_AVAILABLE
        }
        
        self.results['manipulation'] = manipulation
        return manipulation
    
    def generate_map(self):
        if 'gps' not in self.results:
            return None
        
        if not FOLIUM_AVAILABLE or folium is None:
            return None
        
        try:
            gps = self.results['gps']
            m = folium.Map(location=[gps['latitude'], gps['longitude']], zoom_start=15)
            folium.Marker(
                [gps['latitude'], gps['longitude']],
                popup=f"📍 Location",
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
            
            map_path = os.path.join(app.config['UPLOAD_FOLDER'], f"map_{datetime.now().timestamp()}.html")
            m.save(map_path)
            return map_path
        except Exception:
            return None
    
    def _format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size //= 1024
        return f"{size:.1f} TB"
    
    def run_full_analysis(self):
        self.analyze_basic_info()
        self.extract_exif()
        self.generate_hashes()
        self.analyze_colors()
        self.detect_manipulation()
        return self.results


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    if file.filename is None or file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.content_type or not file.content_type.startswith('image/'):
        return jsonify({'error': 'File must be an image'}), 400
    
    try:
        original_filename = file.filename or 'unknown.jpg'
        filename = secure_filename(original_filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        saved_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
        file.save(filepath)
        
        analyzer = ImageAnalyzer(filepath)
        results = analyzer.run_full_analysis()
        
        results['filepath'] = saved_filename
        
        if 'gps' in results:
            map_path = analyzer.generate_map()
            if map_path:
                results['map_path'] = os.path.basename(map_path)
        
        with open(filepath, 'rb') as f:
            img_data = base64.b64encode(f.read()).decode('utf-8')
            content_type = file.content_type or 'image/jpeg'
            results['image_data'] = f"data:{content_type};base64,{img_data}"
        
        results_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{saved_filename}_results.json")
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        return jsonify({
            'success': True, 
            'results': results,
            'redirect': url_for('show_results', filename=saved_filename)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/results/<filename>')
def show_results(filename):
    try:
        results_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}_results.json")
        if os.path.exists(results_path):
            with open(results_path, 'r') as f:
                results = json.load(f)
        else:
            return redirect(url_for('index'))
        
        return render_template('results.html', 
                             results=results,
                             analysis_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        return f"Error: {e}", 404


@app.route('/map/<filename>')
def serve_map(filename):
    map_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(map_path):
        return send_file(map_path)
    return 'Map not found', 404


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500


if __name__ == '__main__':
    print("\n" + "="*50)
    print("🔍 Image Analyzer")
    print("   Built by Hidden_Rhythm")
    print("="*50)
    print(f"🌐 http://127.0.0.1:5000")
    print("="*50 + "\n")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
    except KeyboardInterrupt:
        print("\n✅ Stopped.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)