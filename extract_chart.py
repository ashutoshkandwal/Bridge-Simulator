"""
CAB to PNG/JPG Extraction Helper
Extracts chart images from Gibraltar Strait.cab and places them in the areas folder
"""

import os
import subprocess
import shutil
from pathlib import Path

def extract_cab_windows():
    """Use Windows built-in expand command to extract CAB"""
    areas_path = Path(__file__).parent / "bridge_sim" / "areas"
    cab_file = areas_path / "Gibraltar Strait.cab"
    
    if not cab_file.exists():
        print(f"❌ CAB file not found: {cab_file}")
        return False
    
    print(f"📦 Extracting: {cab_file.name}")
    print(f"   Size: {cab_file.stat().st_size / (1024**2):.1f} MB")
    print("   This may take a minute...")
    
    try:
        result = subprocess.run(
            f'expand "{cab_file}" -F:* .',
            cwd=str(areas_path),
            shell=True,
            capture_output=True,
            text=True
        )
        
        print("✓ Extraction complete!")
        
        # Look for extracted images
        image_dir = areas_path / "Area Spec" / "Gibraltar Strait" / "Images"
        if image_dir.exists():
            images = list(image_dir.glob("*.jpg"))
            print(f"\n✓ Found {len(images)} chart images:")
            for img in images:
                print(f"  • {img.name}")
                # Copy to areas root
                dest = areas_path / img.name.lower()
                shutil.copy2(img, dest)
                print(f"    → Copied to: {dest.name}")
            return True
        else:
            print(f"⚠ Could not find extracted images in {image_dir}")
            print("   The CAB file may need manual extraction.")
            return False
            
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return False

def extract_cab_python():
    """Alternative: Try to extract using Python zipfile (sometimes works)"""
    try:
        import zipfile
    except ImportError:
        print("❌ zipfile module not available")
        return False
    
    areas_path = Path(__file__).parent / "bridge_sim" / "areas"
    cab_file = areas_path / "Gibraltar Strait.cab"
    
    if not cab_file.exists():
        print(f"❌ CAB file not found: {cab_file}")
        return False
    
    print(f"📦 Attempting Python ZIP extraction of: {cab_file.name}")
    
    try:
        with zipfile.ZipFile(cab_file, 'r') as zip_ref:
            # List all files
            all_files = zip_ref.namelist()
            jpg_files = [f for f in all_files if f.lower().endswith('.jpg')]
            
            if jpg_files:
                print(f"✓ Found {len(jpg_files)} JPG files in archive:")
                for jpg_name in jpg_files[:10]:  # Show first 10
                    print(f"  • {jpg_name}")
                    zip_ref.extract(jpg_name, areas_path)
                
                if len(jpg_files) > 10:
                    print(f"  ... and {len(jpg_files) - 10} more")
                
                print(f"\n✓ Extracted to: {areas_path}")
                return True
            else:
                print("⚠ No JPG files found in archive")
                return False
                
    except zipfile.BadZipFile:
        print("⚠ CAB file is not a valid ZIP archive (this is normal)")
        print("   Use Windows expand command or manual extraction instead")
        return False
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return False

def list_extracted_images():
    """List all images in areas folder"""
    areas_path = Path(__file__).parent / "bridge_sim" / "areas"
    
    images = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
        images.extend(areas_path.glob(f"**/{ext}"))
        images.extend(areas_path.glob(f"**/{ext.upper()}"))
    
    if images:
        print("\n📊 Chart Images Found:")
        for img in sorted(images):
            rel_path = img.relative_to(areas_path)
            size_mb = img.stat().st_size / (1024**2)
            print(f"  • {rel_path} ({size_mb:.1f} MB)")
        return len(images)
    else:
        print("\n⚠ No chart images found in areas folder yet")
        return 0

def main():
    print("=" * 60)
    print("Gibraltar Strait CAB Extraction Tool")
    print("=" * 60)
    
    areas_path = Path(__file__).parent / "bridge_sim" / "areas"
    
    if not areas_path.exists():
        print(f"❌ Areas folder not found: {areas_path}")
        return
    
    # Check if CAB exists
    cab_file = areas_path / "Gibraltar Strait.cab"
    if not cab_file.exists():
        print(f"❌ CAB file not found at: {cab_file}")
        return
    
    print(f"\n📁 Working directory: {areas_path.name}/")
    print(f"📦 CAB file: Gibraltar Strait.cab ({cab_file.stat().st_size / (1024**2):.1f} MB)")
    
    # Try Windows extraction first
    print("\n[1/2] Attempting Windows expand command...")
    if extract_cab_windows():
        list_extracted_images()
        print("\n✅ SUCCESS! Your chart images are ready for ECDIS.")
        print("\n📝 Next steps:")
        print("   1. Restart the simulator: python -m bridge_sim.main")
        print("   2. Enter your ship position in the menu")
        print("   3. Navigate to ECDIS (press SPACE twice)")
        print("   4. Your chart should display with the ship marker!")
        return
    
    print("\n[2/2] Attempting Python ZIP extraction...")
    if extract_cab_python():
        list_extracted_images()
        print("\n✅ SUCCESS! Your chart images are ready for ECDIS.")
        return
    
    # If both failed, provide manual instructions
    print("\n" + "=" * 60)
    print("❌ Automatic extraction failed")
    print("=" * 60)
    print("\n📖 Manual Extraction Steps:")
    print("\n1. Open File Explorer")
    print(f"2. Navigate to: {areas_path}")
    print("3. Right-click 'Gibraltar Strait.cab'")
    print("4. Select 'Extract All...'")
    print("5. Choose a destination folder")
    print("6. Navigate to: Area Spec\\Gibraltar Strait\\Images\\")
    print("7. Copy Gibraltar.jpg (or All.jpg) to the areas folder")
    print("8. Rename to: gibraltar.jpg")
    print("9. Restart the simulator")
    print("\nOr see AREAS_GUIDE.md for more options!")

if __name__ == "__main__":
    main()
