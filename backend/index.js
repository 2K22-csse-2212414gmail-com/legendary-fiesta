const express = require('express');
const path = require('path');
const cors = require('cors');
const app = express();

const PORT = 3000;

// ✅ Serve frontend folder
app.use(cors());
app.use(cors({
  origin: "http://localhost:3000" // your frontend origin
}));

app.use(express.json());
app.use(express.static(path.join(__dirname, '../frontend')));

// ✅ Routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../frontend/index.html'));
});

app.get("/home", (req, res) => {
    res.sendFile(path.join(__dirname, '../frontend/home.html'));
    
});
app.get('/about', (req, res) => {
  res.sendFile(path.join(__dirname, '../frontend/about.html'));
});

app.get('/contact', (req, res) => {
  res.sendFile(path.join(__dirname, '../frontend/contact.html'));
});
app.post('/contact', (req, res) => {
  const { name, email, message } = req.body;
  console.log(name, email, message);

  // Here you can save to DB or send email
  res.status(200).json({ message: "Message received" });
});
app.get('/app', (req, res) => {
  res.redirect("http://localhost:8501");
})

app.listen(PORT, () => {
  console.log(`✅ Server running at http://localhost:${PORT}`);
});
