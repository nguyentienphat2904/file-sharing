import express, { Request, Response } from "express";
import dotenv from "dotenv";
import fileRouter from "./routes/file.route";
import peerRouter from "./routes/peer.route";

dotenv.config();

const app = express();
const port = process.env.PORT;

const mongoose = require("mongoose");

app.use(express.json());

app.get('/', (req: Request, res: Response) => {
    res.send('Like-torrent app')
});

app.use('/api/files', fileRouter);
app.use('/api/peers', peerRouter);

mongoose.connect(process.env.MONGO_URL)
    .then(() => {
        console.log("Connected to database");
        app.listen(port, () => {
            console.log(`Server is running on http://localhost:${port}`);
        });
    })
    .catch(() => {
        console.log("Error connected to database");
    });