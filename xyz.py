import ezdxf

# Create a new DXF document
doc = ezdxf.new(dxfversion="R2010")
msp = doc.modelspace()

# === BASE DIMENSIONS ===
base_length = 120  # mm
base_width = 80    # mm

# === DRAW BASE RECTANGLE ===
msp.add_lwpolyline([
    (0, 0), 
    (base_length, 0),
    (base_length, base_width),
    (0, base_width),
    (0, 0)
], close=True)

# === RFID SCANNER SLOT (65x35mm, Top Center) ===
rfid_w, rfid_h = 65, 35
rfid_x = (base_length - rfid_w) / 2
rfid_y = base_width - 5  # 5mm from top edge
msp.add_lwpolyline([
    (rfid_x, rfid_y),
    (rfid_x + rfid_w, rfid_y),
    (rfid_x + rfid_w, rfid_y - rfid_h),
    (rfid_x, rfid_y - rfid_h),
    (rfid_x, rfid_y)
], close=True)

# === FINGERPRINT SENSOR SLOT (14x18mm, Centered) ===
fp_w, fp_h = 14, 18
fp_x = (base_length - fp_w) / 2
fp_y = (base_width - fp_h) / 2
msp.add_lwpolyline([
    (fp_x, fp_y),
    (fp_x + fp_w, fp_y),
    (fp_x + fp_w, fp_y + fp_h),
    (fp_x, fp_y + fp_h),
    (fp_x, fp_y)
], close=True)

# === USB SLOT (12x6mm, Bottom Center) ===
usb_w, usb_h = 12, 6
usb_x = (base_length - usb_w) / 2
usb_y = 0  # bottom edge
msp.add_lwpolyline([
    (usb_x, usb_y),
    (usb_x + usb_w, usb_y),
    (usb_x + usb_w, usb_y + usb_h),
    (usb_x, usb_y + usb_h),
    (usb_x, usb_y)
], close=True)

# === MOUNTING HOLES (4 Corners, 3mm screw = 1.5mm radius) ===
hole_r = 1.5
offset = 5  # distance from corner
msp.add_circle((offset, offset), hole_r)
msp.add_circle((base_length - offset, offset), hole_r)
msp.add_circle((offset, base_width - offset), hole_r)
msp.add_circle((base_length - offset, base_width - offset), hole_r)

# === VENTILATION GRID (2mm holes, 3 rows x 5 cols) ===
vent_rows = 3
vent_cols = 5
vent_spacing_x = 6
vent_spacing_y = 6
vent_start_x = (base_length - (vent_cols - 1) * vent_spacing_x) / 2
vent_start_y = 20
for i in range(vent_cols):
    for j in range(vent_rows):
        cx = vent_start_x + i * vent_spacing_x
        cy = vent_start_y + j * vent_spacing_y
        msp.add_circle((cx, cy), 1)  # 2mm diameter holes

# === EMBOSSED LABEL ===
text = msp.add_text("ATTENDANCE SYSTEM", dxfattribs={
    "height": 5
})
text.dxf.insert = (30, 5)


# === SAVE DWG FILE ===
doc.saveas("attendance_case_v2.dwg")
print("✅ DWG file saved as 'attendance_case_v2.dwg'")
