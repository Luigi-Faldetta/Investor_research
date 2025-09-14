# Cloudinary Setup Guide for Investor Photos

## 1. Create Cloudinary Account

1. Go to https://cloudinary.com
2. Sign up for a free account (gives you 25GB storage + 25GB monthly bandwidth)
3. After registration, go to your Dashboard

## 2. Get Your Credentials

From your Cloudinary Dashboard, copy:
- **Cloud Name** (e.g., `your-cloud-name`)
- **API Key** (e.g., `123456789012345`)
- **API Secret** (e.g., `abcdefghijklmnopqrstuvwxyz123456`)

## 3. Add to Environment Variables

Add these to your `.env` file:

```bash
# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=123456789012345  
CLOUDINARY_API_SECRET=abcdefghijklmnopqrstuvwxyz123456
```

## 4. Upload Investor Photos

Run the setup script to upload high-quality investor photos:

```bash
pipenv run python third_parties/cloudinary_setup.py
```

Choose option 1 to upload all photos. The script will:
- Download high-quality photos from reliable sources
- Resize and optimize them (400x400, face-focused cropping)
- Upload to your Cloudinary account
- Generate reliable URLs

## 5. Verify Upload

After uploading, you can:
- Check option 2 to list all uploaded photos
- Check option 3 to test individual photo retrieval
- View photos in your Cloudinary Media Library

## 6. Benefits of Cloudinary

✅ **Reliable hosting** - 99.9% uptime  
✅ **Automatic optimization** - WebP, AVIF formats, smart compression  
✅ **Fast CDN delivery** - Global edge locations  
✅ **Face detection** - Automatic cropping focused on faces  
✅ **Responsive images** - Automatic resizing for different devices  
✅ **Free tier** - 25GB storage, 25GB bandwidth/month  

## 7. How It Works

The system now uses this priority order:

1. **Cloudinary URLs** (highest quality, most reliable)
2. **Curated URLs** (backup reliable sources)  
3. **Tavily image search** (dynamic discovery)
4. **Generated avatars** (guaranteed fallback)

## 8. Adding New Investors

To add new investors:

1. Add their photo URLs to `get_high_quality_investor_photos()` in `cloudinary_setup.py`
2. Run the upload script again
3. The new photos will be automatically available

## 9. Cost Estimate

**Free tier includes:**
- 25GB storage (thousands of investor photos)
- 25GB monthly bandwidth
- 25,000 transformations/month

**If you exceed free tier:**
- Storage: $0.10/GB/month
- Bandwidth: $0.06/GB
- Transformations: $0.0018/1000

For a typical investor research app, you'll likely stay within the free tier.

## 10. Troubleshooting

If photos don't appear:
1. Check your `.env` file has correct credentials
2. Run the test script to verify connection
3. Check Cloudinary dashboard for uploaded photos
4. Verify URLs in browser

The system will automatically fall back to avatar generation if Cloudinary fails.