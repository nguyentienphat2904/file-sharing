import express, { Request, Response } from "express";
import { FileController } from "../controller/file.controller";

const router = express.Router();
const fileController = new FileController();

router.get('/fetch', fileController.fetch); // fetch all file
router.post('/publish', fileController.publish); // publish peer's file

export default router;