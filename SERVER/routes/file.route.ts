import express, { Request, Response } from "express";
import { FileController } from "../controller/file.controller";

const router = express.Router();
const fileController = new FileController();

router.get('/fetch', fileController.search); // fetch all file
router.post('/publish', fileController.upload); // fetch all file

export default router;