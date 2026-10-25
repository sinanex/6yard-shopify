const fs = require('fs');
const mongoose = require('/Users/mac/6yard-nextjs/node_modules/mongoose');

async function main() {
  const envContent = fs.readFileSync('/Users/mac/6yard-nextjs/.env', 'utf8');
  const match = envContent.match(/MONGO_URI=([^\r\n]+)/);
  if (!match) {
    console.error('No MONGO_URI found in .env');
    return;
  }
  const uri = match[1].trim().replace(/^['"]|['"]$/g, '');
  await mongoose.connect(uri);
  const db = mongoose.connection.db;
  
  // 1. From reviews collection
  const reviewsCol = await db.collection('reviews').find({}).toArray();
  console.log(`Found ${reviewsCol.length} reviews in 'reviews' collection.`);

  // 2. Also check if products collection has embedded reviews
  const productsWithReviews = await db.collection('products').find({ 'reviews.0': { $exists: true } }).toArray();
  console.log(`Found ${productsWithReviews.length} products with embedded reviews.`);

  let allEmbedded = [];
  productsWithReviews.forEach(p => {
    if (Array.isArray(p.reviews)) {
      p.reviews.forEach(r => {
        allEmbedded.push({
          ...r,
          productId: p._id,
          productName: p.name,
          productImage: (p.images && p.images[0]) || '',
          team: p.team || ''
        });
      });
    }
  });
  console.log(`Total embedded reviews: ${allEmbedded.length}`);

  fs.writeFileSync(
    '/Users/mac/6yard-shopify/scripts/extracted_reviews.json',
    JSON.stringify({ directReviews: reviewsCol, embeddedReviews: allEmbedded }, null, 2)
  );
  console.log('Saved to /Users/mac/6yard-shopify/scripts/extracted_reviews.json');

  await mongoose.disconnect();
}

main().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
