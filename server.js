import express from 'express';
import cors from 'cors';
import reviewRouter from './api/review.js';

const app = express();

app.use(cors());
app.use(express.json());

app.use('/api', reviewRouter);

app.listen(5501, () => {
  console.log('API server running at http://localhost:5501');
});

