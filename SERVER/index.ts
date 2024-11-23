import express, { NextFunction, Request, Response } from "express";
import dotenv from "dotenv";
import fileRouter from "./routes/file.route";
import peerRouter from "./routes/peer.route";
import authRouter from "./routes/auth.route";
import { authMiddleware } from "./middleware/auth.middleware";

dotenv.config();

const app = express();
const port = process.env.PORT;

const mongoose = require("mongoose");

app.use(express.json());

app.get('/', (req: Request, res: Response) => {
    res.send('Like-torrent app')
});

app.use('/api/files', authMiddleware, fileRouter);
app.use('/api/peers', authMiddleware, peerRouter);
app.use('/api/auth', authRouter)

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