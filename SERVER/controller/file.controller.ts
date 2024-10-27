import { Request, Response } from "express";
import { FileModel } from "../models/file.model";

export class FileController {

    async search(req: Request, res: Response): Promise<void> {
        try {
            const files = await FileModel.find({});
            res.status(200).json({
                success: true,
                message: "Fetch all Files",
                data: files
            });
        } catch (error: any) {
            res.status(500).json({
                success: false,
                message: error.message,
                data: []
            });
        }
    };

    async upload(req: Request, res: Response): Promise<void> {
        try {
            const file = await FileModel.create(req.body);
            res.status(200).json({
                success: true,
                message: "Upload file sucessfully",
                data: file
            });
        } catch (error: any) {
            res.status(500).json({
                success: false,
                message: error.message,
                data: []
            });
        }
    }
}